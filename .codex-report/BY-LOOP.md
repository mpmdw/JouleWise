# BY-LOOP — local implementation in progress

## PROGRESS

- DONE: local intake at clean 17983dcb3; no active stop card. Added configs/b6/loop_bytes.json (twelve explicit pack_ids and BYTES order, dedicated root), loop discovery filter and CLI config-root default with explicit/env override retained. First full tests.test_b6_loop run: 57 tests, 32.572 s, OK (before guard addition); final 58 tests, 23.646s, OK.
- DONE: DONE guard uses native zsh state read plus done.idle, published after successful final I/O. Explicit state change invalidates skip. Focused three new tests passed, 0.076 s; argv sentinel proves DONE invokes no tick executable.
- NEXT: scratch rehearsal PASSED (root /private/tmp/jwtmp-byloop.VDqS8u; rehearsal.json), using tests.b6.round_support.bytes_rehearsal. Full loop rerun after guard PASSED: 58 tests, 23.646s, exit 0 (before final pending-outbox refinement). It uses real runpy entry point, open_packs, driver preparation and smoke.prepare; only hardware identity/precheck, transport and launch are synthetic. Next item 4 fails-before/passes-after; leak trace and module runs. Item 48 relay audit completed: no in-scope yield LOW relay found.
- CHECKPOINT: DONE outbox retry edge hardened after full run: mailer records failures internally, so loop checks pending delivery/close entries before publishing done.idle. Two focused guard/retry tests passed (0.032s); full module rerun after this last change still pending.
- OPEN: production BYTES sizing is absent from configs/b6/registration/sizing_b5.json (DriverLane requires plan_inputs.build sizing). Scratch may supply synthetic sizing; real C5 sizing remains an external registration gate. Historical cloud sections below need replacement as steps finish. No scope request yet. Director owns commits/pushes/CI. All existing edits are this slice's.

## SUMMARY

- Status: PARTIAL local implementation. Dedicated BYTES queue, CLI config-root selection, DONE guard and real-entry-point scratch rehearsal passed. Items 4/5 and remaining module/audit work pending.
- Base confirmed through connected GitHub: `bda481d5af510b29dde4976f172a20170a42c955`.
- BY-INT's lane head still equals that base; no base movement was observed.
- No earlier BY-LOOP lane branch existed when checked.
- Governing block-6 and BYTES registration texts were read; a dedicated BYTES root is the implementation choice below.
- Item 48's live yield notice is built inside the sealed block-5 driver; the authorized known-false-alarm disposition is recorded.
- The duplicate close notice is traced to the magistrate's manual step; loop wake remains the chosen single owner.
- Only scoped production/test/config/report files changed; production registrations, measurement state and sealed files remain untouched.
- Initial loop module: 57 tests passed; three focused root/config/guard tests passed. Rehearsal passed. Stage-success and leak fixes remain pending.

## LOOP ROOT CHOICE

Dedicated root implemented in configs/b6/loop_bytes.json: `/Users/edr/night-b6/loop-bytes`. Production directory never accessed or created.

Authority: `docs/design/block6_collection_draft.md` §6.1 closes once every pack has its target, and §14 makes the pack the unit of registration, collection and release with a queue of open packs. `docs/registrations/block6_replication_DRAFT.md` §14 S-2 identifies the existing replication loop root. `docs/registrations/bytes_pack_v1.md` §5 fixes twelve independent, fixed, one-session packs and order s1-p1 through s6-p1, then s6-p2 through s1-p2; its authority paragraph requires replication behavior to remain byte-identical.

The dedicated root preserves the replication loop's DONE history and avoids inventing a DONE-to-NEXT reopening rule. Its configuration restricts discovery to the twelve BYTES packs so existing replication registrations cannot be recollected. All twelve belong to the same active BYTES queue. No state under the proposed production path or the existing production root has been read or written by this seat.

## ITEMS

### 1. Twelve-pack loop readiness

Implemented configs/b6/loop_bytes.json with dedicated root, twelve-pack order and explicit pack_ids. loop.py filters discovery to those ids; scripts/b6_loop.py uses selected config root after CLI/environment override. Tests cover discovery and root precedence. tests/b6/round_support.py adds real-entry-point rehearsal helper.

Observed: the default order already includes all twelve BYTES packs, DONE remains terminal in `Loop.tick`, and a fresh root starts at NEXT. Production BYTES registrations at the base remain draft; synthetic rehearsal copies must be explicitly registered-shaped and committed only in scratch.

### 2. DONE tick overhead

Implemented loop.py done.idle publication after successful final mail/wake I/O and an empty pending outbox (delivery or close). Native-zsh guard reads DONE and marker then exits before Python. Explicit state change lets it fall through. NEXT with no open packs still discovers future registrations. Existing DONE roots get the marker on first successful updated tick.

### 3. Item 48: smoke yield notice

**Recorded known false alarm; sealed code left unchanged.**

At base `bda481d5a`, `joulewise/b5/driver.py:1418` builds `yield_plan` from dispatch run IDs, not the reduced tree's kept counts. Its `count_stage` compares succeeded members with `_min_valid(role, planned)`, and `YieldTripwire` owns the live notice; `execute` calls `yield_plan` and constructs that tripwire. The smoke reduces dispatch execution after order resolution in `joulewise/b6/smoke.py`, using `configs/b6/smoke_keep.json`; the full order manifests deliberately remain intact.

Consequently the historical 3/10/10/3 plan can classify four successful one-member smoke stages as LOW. Computing a desk-only kept-count summary in smoke.py would not correct the live driver notice. The item brief expressly allows recording the false alarm when notice construction is confined to driver.py. No threshold, printed quantity, exclusion, or block-5 byte is changed. This item is a source-based disposition, not a successful live smoke test. Local relay audit of smoke.py, loop.py and mailer.py found no LOW/yield alert or desk line relaying the driver count; smoke.py uses yield only as a Python generator in _flag_codes. loop smoke desk carries acceptance status/codes and mailer has no yield relay. Keep the recorded false alarm; no alternative printed number was introduced.

### 4. Item 52 / issue 509: explained anchor fallback

Not implemented: executor unavailable. `smoke.stages_succeeded` currently explains campaign rc 1 only for recorded idle skips, after exact stage/member dispatch matching. Its desk caller also gates that explanation on idle flags. The fix must cover the caller as well as the helper, retain exact membership checks, and reject every other failed-member cause. Fails-before / passes-after evidence remains required.

### 5. Leaked hazard monitor

Not fixed or reproduced: executor unavailable. Read `tests/b6/test_s3_cold_fixes.py`, `tests/test_fixture_orphan_census.py`, and `tests/b6/support.py`. The named cold-fix module has no direct Popen call at the base, so the originating process must be traced through its exercised seams or the broader s3-cold execution before asserting a cause. Do not claim the leak is repaired merely because the module contains no direct spawn. The fixture orphan census and a bounded fails-before / passes-after run remain required.

### 6. Duplicate block-6 close mail

**Recorded; no mailer change. Loop wake is the single owner of the close notice.**

`docs/process_traces/2026-10-21-magistrate-283e9802/RECORD.md`, “Block 6 closed” and “Pruning list”, explicitly identifies the magistrate's manual “email the verdict” instruction as the second sender. `RUN_STATE.md` items 59 and 60 also distinguish the loop wake and that activation. `Loop._next` has one close event; the scoped `joulewise/b6/mailer.py` provides outbox delivery and issue closing, and has no magistrate-specific close dispatcher to prune.

This is a manual orchestration-instruction duplication, so changing the shared mailer would affect the existing loop delivery rather than removing the magistrate's instruction. The historical prose is evidence, not a second executable mailer. No in-scope magistrate sender was identified. The lead should carry loop-wake ownership into the external activation instructions; the requested record-only disposition is used here. No message was sent by this seat.

## REHEARSAL

Local PASS, scratch root /private/tmp/jwtmp-byloop.VDqS8u. Replay from repository root:

```sh
JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B - <<'PY'
import os
from pathlib import Path
from tests.b6.round_support import bytes_rehearsal
print(bytes_rehearsal(Path(os.environ['TMPDIR'])))
PY
```

Exit 0. Layout: measurement/{configs,joulewise,scripts,.git,.venv}, loop.json, loop-bytes/{state.json,staging}, bin/launchctl, launchctl.argv, rehearsal.json. Twelve registered-shaped synthetic registrations and full plan/config trees committed only in scratch. Three calls through real scripts/b6_loop.py via runpy; real open_packs, composition, DriverLane preparation and smoke.prepare. Hardware identity/precheck, transport, stop-ref network observation and launch are synthetic seams. Fake first on PATH and driver.launchctl_bin set to it. Launch executes only fake; no install/arm.

Observed: NEXT → PRECHECK → SMOKE_RUN → SMOKE_RUN. Discovered 12; selected bytes-s1-p1; prepared r1-bytes-s1-p1-smoke-0. Isolated smoke clone, reduced tree, copied ledger/pin, wrapper and session.json exist. Deferred plan path ends smoke/bytes-s1-p1-20261022T0758Z/custody/night_plan.json. Fake argv log: `rehearsal-only r1-bytes-s1-p1-smoke-0`.

Fixture sizing copies ALPHA allowances explicitly; max_s=124620 is a synthetic formula result, not BYTES sizing evidence. Production C5 sizing is absent and remains external. First attempt repeated NEXT because runner omitted capture_output/text defaults; fixed runner and replay passed. Director independent repetition remains outstanding.

## DONE TICK

Native-zsh DONE plus done.idle fast path skips the tick executable. test_done_guard_skips_tick_and_resume_invalidates supplies JW_B6_LOOP_TICK as harmless touch of python-started sentinel: guard exits 0 in DONE with no sentinel, then creates sentinel with state NEXT. Marker published only after successful final I/O; first updated DONE tick creates it, subsequent ticks skip Python.

## TESTS RUN

Repository cwd; each command uses fresh TMPDIR and synthetic-only:

```sh
JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_b6_loop
```

Initial run exit 0: 57 tests in 32.572s, OK (before DONE guard addition). Final rerun exit 0: 58 tests in 23.646s, OK; no skips.

```sh
JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_b6_loop.LoopTests.test_dedicated_bytes_config_limits_discovery_and_starts_next tests.test_b6_loop.LoopTests.test_cli_config_root_and_explicit_override tests.test_b6_loop.LoopTests.test_done_guard_skips_tick_and_resume_invalidates
```

Exit 0: 3 tests in 0.076s, OK, no skips. Rehearsal above exit 0. No whole suite. Stages/leak fails-before/passes-after pending.

`pgrep -fl hazard_monitor`: exit 3; `sysmon request failed with error: sysmond service not found`; `pgrep: Cannot get process list`. No processes killed. Need usable process evidence for leak investigation.

After final outbox refinement: `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_b6_loop.LoopTests.test_done_dormancy_waits_for_outbox_retry tests.test_b6_loop.LoopTests.test_done_guard_skips_tick_and_resume_invalidates`: exit 0, 2 tests in 0.032s, OK. `git diff --check`: exit 0.

## SEALED INVENTORY

682 paths. Local working-tree-inclusive intersection of inventory files with `git diff --name-only bda481d5a` plus `git ls-files --others --exclude-standard`: sealed_paths: 682; changed_overlap: []. No sealed file changed. After director commit, required committed check is `git diff --name-only bda481d5a HEAD` against the same inventory.

## CI

Draft PR **#542**, `ci/2026-10-22-bytes-loop` against main, titled “CI: BYTES loop readiness (BY-LOOP)”: https://github.com/mpmdw/JouleWise/pull/542.

Checkpoint `c2a7dd5025079c2ab01bc5aaf2ea845434171c2b` was verified as the exact head of both lane and CI branch through connected GitHub. Its CI workflow was observed pending (run 39743424315); gate-ledger completed with failure (run 39743424387). The failure reason was not inspected; no claim of green checks is made. The earlier report checkpoint had both workflows in progress. This final commit changes only the report and is fast-forwarded to the CI branch as well. No code-readiness result is claimed; the PR body explicitly says implementation and execution remain blocked. Do not merge.

## DECISIONS I MADE

- Use a dedicated BYTES root rather than reopening the replication loop, for the governing reasons above; implementation and scratch rehearsal are complete.
- Record item 48's known live LOW false alarm under the brief's explicit sealed-driver exception.
- Keep loop wake as the single owner of close notification; record the external/manual magistrate duplication without changing the shared mailer.
- Preserve cloud source findings; local slice now supplies filesystem execution evidence.
- Do not substitute unit-only, remote source-reading or historical evidence for the required synthetic real-entry-point rehearsal.

## OPEN ISSUES

- Item 4 stages_succeeded/caller and item 5 leak remain pending. Item 48 relay audit complete; recorded false alarm retained.
- Remaining scoped modules and hazard censuses pending.
- Production BYTES C5 sizing absent; scratch values are synthetic only.
- Director independent rehearsal, final review, commit/push and CI refresh outstanding.

## NEEDS_RULING

none. Runtime availability is an infrastructure blocker, not a scientific ruling.
