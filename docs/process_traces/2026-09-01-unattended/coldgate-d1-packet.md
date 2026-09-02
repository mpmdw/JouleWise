# COLD-GATE PACKET — night driver D1 (dead-man vs. empty chain.started marker)

Mechanically assembled by the magistrate on 2026-09-01 from: luna report 132 (verbatim finding), terra report 130 F3 (verbatim), the ruling text R-3/R-7/§8 d.3, and `scripts/run_night.py` at `f07c85d5` (verbatim excerpts, line-numbered). No magistrate commentary appears before §5.

## 1. Luna 132 (delta re-audit of fix round 3) — verdict FIX-ROUND, blocker D1
```
The blocker is the timing race: `_claim_chain_start` creates an empty marker before `Popen`. Dead-man can observe that marker at `1281-1288`, write `chain.exited`, and launch the courier while `Popen` is still starting. If `Popen` then succeeds, the real chain is alive during courier execution; if it fails, both paths can race to create `chain.exited`.
## Residual risk

`_next_deadman_epoch` protects the normal run-path calculation for `t0 >= 07:00` by selecting the next civil day, but `dead_man()` itself has no explicit pre-`t0` guard. That adjacent behavior predates this delta and was not counted as the blocker.
```

## 2. Terra 130 F3 (the finding fix round 3 cured) — verbatim from brief run-wo2-fix3.md
```
F3 — **A chain `Popen` failure loses the night.** `scripts/run_night.py:385`:
an `OSError` (ENOENT, EMFILE, EACCES) from `subprocess.Popen` is raised
AFTER the O_EXCL `chain.started` claim and BEFORE `_complete_chain_start`,
so the night ends with a zero-byte `chain.started`, no `chain.exited`, no
result, no durable push, no courier — and the dead-man then reads the empty
marker as a live chain and refuses the courier too. Cure:
- Wrap the `Popen` in `try/except OSError`. On failure: complete the marker
  honestly (`chain.started` gets `{"pid": null, "pgid": null, "epoch_s",
  "launch_error": "<class>: <text>"}`), write `chain.exited` with
  `{"exit_code": null, "launch_failed": true, "epoch_s"}` so the dead-man's
  "chain has exited" reading is true, then the ordinary refusal path with a
  NEW driver code `night_chain_launch_failed` (add it to
  `NIGHT_DRIVER_REASON_CODES`, sorted position, comment in the same style),
  durable record, courier, non-zero exit (`EXIT_REFUSED` or a distinct code —
  say which and why).
- The dead-man must treat a `chain.started` whose `pgid` is null or whose
  file is empty/unparseable as NOT a live chain: with `chain.exited` present
  it proceeds to courier; with `chain.exited` absent it writes
  `chain.exited` `{"reaped_by": "dead-man", "launch_failed": true, …}` and
  proceeds. Never `killpg` on a null pgid.
- Tests: (1) `Popen` raising `FileNotFoundError` → `night_chain_launch_failed`
  refusal validates under `validate_refusal`, `chain.exited.launch_failed is
  True`, courier attempted, push attempted, rc non-zero; (2) dead-man over a
  fixture with an EMPTY `chain.started` and no `chain.exited` → couriers, no
  `killpg` call; (3) the same with a null-pgid marker.
```

## 3. Ruling text (MAGISTRATE-RULING-UNATTENDED-STAGE1.md)
```
**R-3 — the census is the driver's first act and uses the production
predicate.** The predicate is `/usr/bin/pgrep -lf "codex|claude|t3"` with exit
status exactly 1 and empty stdout (`arm_readiness_evidence_t0.py:1312-1314`,
`:1724`). Any other outcome refuses the night with
`night_refused_agent_present` and the offending lines are written into the
result record. Today at the bench that command returns 586 lines — this
session, the Codex seats, T3 Code — which is exactly why the interactive
session must be gone before the timer fires (R-9). The agent's exit is
proven by this census, never by a self-report: the "agent-exit" record the
...
111:07:00 runs the driver in `--dead-man` mode (R-7).
125:**R-7 — reporting without any channel in the repo (G-11).** No file in the
253:  "measure first." **Opus's method wins**, Fable's ceiling kept; R-7.
**R-7 — reporting without any channel in the repo (G-11).** No file in the
repo can send email. Stage 1 therefore uses two layers, neither of which is
"a script emails Ed":
- **Durable record, no agent:** the driver commits `night_result.json` (and
  the receipt, refusal, censuses) to branch `night-results/<date>` and pushes
  it — from a fresh shallow clone under the custody root, never by checking
  out a branch in the development tree (that would move the HEAD R-6 binds
  to). That branch is readable from a phone and survives every later failure.
- **Courier:** after the chain exits (or after any refusal) the driver
  launches a headless `claude -p` session — the **courier** — whose prompt
  is fixed text: read `NIGHT_HANDBACK.md`, read the result record, email Ed
  (Gmail `send_message` to his own address — the only channel that reaches
  him), then resume the loop. Liveness proof: the courier's first scripted
  act writes `courier.heartbeat` (pid, monotonic ns); the driver stands down
  only on that file; otherwise it retries up to 3 times with backoff
  60/180/600 s. The **dead-man** (07:00 calendar entry) re-runs the courier
  step alone if `courier.sent` is absent — and REFUSES (`night_chain_alive`)
  while the chain has not exited, because a courier is an agent process and
  starting one during capture breaches the zero-agent fence; the gate also
  requires `t0 + window_max_s + COURIER_DEADLINE_S` to precede the dead-man
  hour (`night_plan_overruns_deadman`). Numbers: the 600 s figure reuses
  T26's magnitude but T26 ruled a T-0 clock-evidence *authoring* bound, not a
  relaunch deadline (`COLD-GATE-RULING.md`); WO-2 measures a cold `claude -p`
  start on this machine and the deadline constant is set to
  `max(3 × measured, 300)` capped at 600, recorded in the trace.

```

§8 d.3 (cold gate on R-10):
```
permissible narrowing, not an Ed-only reversal, provided the stage-1 email
naming the first armed date is SENT before the LaunchAgent is armed and says
the night launches without his hand unless he replies NO; (c) kernel fence
rewording supplied (installed in WO-4 verbatim); **REVERSED for G2-b**
(pack-bound; stays under E-10, moves to stage 3). Refusals d.1–d.6, each
now cured in the text above or bound as stage-2 acceptance: d.1 G2-b
struck from `DIAGNOSTIC_NO_PACK`; d.2 driver never `execve`s; d.3 dead-man
refuses while the chain is alive + overrun predicate; d.4 launchd-path
rehearsal is stage-2 acceptance; d.5 AC-power refusal; d.6 results push from
a fresh clone. The magistrate accepts all six without dissent.

Opus contract-lens refuter (`coldgate-e10-opus.md`): concurs on (a)/(b) and
on the G2-b carve-out; its fence test is "pack/launcher consumption, not the
```

## 4. Code at `f07c85d5` — `scripts/run_night.py` (verbatim, line-numbered)

### 4a. Claim / launch / launch-failure
```python
 301: def _record_chain_exit(
 302:     night_dir: Path,
 303:     exit_code: int | None,
 304:     *,
 305:     reaped_by: str | None = None,
 306:     launch_failed: bool = False,
 307: ) -> None:
 308:     record: dict[str, Any] = {
 309:         "exit_code": exit_code,
 310:         "epoch_s": time.time(),
 311:         "monotonic_ns": time.monotonic_ns(),
 312:     }
 313:     if reaped_by is not None:
 314:         record["reaped_by"] = reaped_by
 315:     if launch_failed:
 316:         record["launch_failed"] = True
 317:     _write_json(night_dir / "chain.exited", record)
 318: 
 319: 
 320: def _terminate_process_group(
 321:     process: subprocess.Popen[Any],
 322:     night_dir: Path | None = None,
 323:     *,
 324:     pgid: int | None = None,
 325: ) -> bool:
 326:     """Return True only when wait() proves that the child session exited."""
 327: 
 328:     process_group = process.pid if pgid is None else pgid
 329:     try:
 330:         os.killpg(process_group, signal.SIGTERM)
 331:     except (ProcessLookupError, PermissionError):
 332:         pass
 333:     try:
 334:         exit_code = process.wait(timeout=30)
 335:     except subprocess.TimeoutExpired:
 336:         try:
 337:             os.killpg(process_group, signal.SIGKILL)
 338:         except (ProcessLookupError, PermissionError):
 339:             pass
 340:         try:
 341:             exit_code = process.wait(timeout=30)
 342:         except subprocess.TimeoutExpired:
 343:             return False
 344:     if night_dir is not None:
 345:         _record_chain_exit(night_dir, exit_code)
 346:     return True
 347: 
 348: 
 349: def _claim_chain_start(night_dir: Path) -> int | None:
 350:     try:
 351:         return os.open(
 352:             night_dir / "chain.started",
 353:             os.O_CREAT | os.O_EXCL | os.O_WRONLY,
 354:             0o600,
 355:         )
 356:     except FileExistsError:
 357:         return None
 358: 
 359: 
 360: def _complete_chain_start(descriptor: int, process: subprocess.Popen[Any]) -> int:
 361:     # start_new_session=True makes the child the process-group leader.
 362:     pgid = process.pid
 363:     try:
 364:         _write_all(
 365:             descriptor,
 366:             _json_bytes({"pid": process.pid, "pgid": pgid, "epoch_s": time.time()}),
 367:         )
 368:     finally:
 369:         os.close(descriptor)
 370:     return pgid
 371: 
 372: 
 373: def _complete_chain_launch_failure(descriptor: int, error: OSError) -> str:
 374:     launch_error = f"{type(error).__name__}: {error}"
 375:     try:
 376:         _write_all(
 377:             descriptor,
 378:             _json_bytes(
 379:                 {
 380:                     "pid": None,
 381:                     "pgid": None,
 382:                     "epoch_s": time.time(),
 383:                     "launch_error": launch_error,
 384:                 }
 385:             ),
 386:         )
 387:     finally:
 388:         os.close(descriptor)
 389:     return launch_error
 390: 
 391: 
 392: def _run_chain_once(
 393:     chain_path: Path,
 394:     plan: NightPlan,
 395:     probes: Probes,
 396:     night_dir: Path,
 397:     claim_descriptor: int,
 398:     *,
 399:     command: list[str] | None = None,
 400:     abort_on_census: bool = True,
 401: ) -> tuple[int | None, dict[str, Any] | None, int, list[dict[str, Any]], bool]:
 402:     """Run exactly one child session and continuously census it."""
 403: 
 404:     census_path = night_dir / "censuses.jsonl"
 405:     stdout_path = night_dir / "chain.stdout.log"
 406:     stderr_path = night_dir / "chain.stderr.log"
 407:     with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
 408:         environment = os.environ.copy()
 409:         environment["NIGHT_PLAN_ID"] = plan.plan_id
 410:         try:
 411:             process = subprocess.Popen(
 412:                 command if command is not None else ["/bin/zsh", str(chain_path)],
 413:                 stdout=stdout,
 414:                 stderr=stderr,
 415:                 env=environment,
 416:                 start_new_session=True,
 417:             )
 418:         except OSError as error:
 419:             launch_error = _complete_chain_launch_failure(claim_descriptor, error)
 420:             _record_chain_exit(night_dir, None, launch_failed=True)
```

### 4b. `_next_deadman_epoch`
```python
 858: def _next_deadman_epoch(t0_epoch_s: float) -> float:
 859:     t0 = datetime.fromtimestamp(t0_epoch_s)
 860:     deadman = t0.replace(
 861:         hour=DEADMAN_HOUR,
 862:         minute=DEADMAN_MINUTE,
 863:         second=0,
 864:         microsecond=0,
 865:     )
 866:     if deadman <= t0:
 867:         deadman += timedelta(days=1)
 868:     return deadman.timestamp()
 869: 
 870: 
 871: def _existing_record(night_dir: Path) -> Path | None:
 872:     return next(
 873:         (night_dir / name for name in _WRITE_ONCE_RECORDS if (night_dir / name).exists()),
 874:         None,
 875:     )
 876: 
 877: 
 878: def _write_rerun_refusal(night_dir: Path, plan: NightPlan, existing: Path) -> None:
 879:     epoch_s = int(time.time())
 880:     path = night_dir / f"rerun-{epoch_s}.refusal.json"
```

### 4c. Dead-man
```python
1253: def dead_man(plan_path: Path, *, courier_bin: Path | None = None) -> int:
1254:     try:
1255:         plan = _load_plan(plan_path)
1256:     except (OSError, ValueError, TypeError, PlanError) as error:
1257:         return _malformed_plan_exit(plan_path, error, courier_bin)
1258:     custody_root = Path(plan.custody_root)
1259:     night_dir = custody_root / "night"
1260:     night_dir.mkdir(parents=True, exist_ok=True)
1261:     sent = night_dir / "courier.sent"
1262:     if sent.exists():
1263:         _fsync_path(sent)
1264:         _append_log(custody_root, "dead-man skipped: courier already sent")
1265:         return EXIT_GO
1266: 
1267:     resolved_courier, courier_error = _resolve_courier_bin(courier_bin)
1268:     if _courier_lock_is_live(night_dir):
1269:         _write_driver_refusal(
1270:             night_dir / "refusal.json",
1271:             plan,
1272:             _CODES["courier_running"],
1273:             "a fresh courier lock belongs to a live process",
1274:         )
1275:         _append_log(custody_root, "dead-man refused while courier was running")
1276:         _durable_record(custody_root, night_dir, plan)
1277:         return EXIT_REFUSED
1278: 
1279:     started = night_dir / "chain.started"
1280:     exited = night_dir / "chain.exited"
1281:     if started.exists() and not exited.exists():
1282:         pgid = _read_started_pgid(started)
1283:         if pgid is None:
1284:             _record_chain_exit(
1285:                 night_dir,
1286:                 None,
1287:                 reaped_by="dead-man",
1288:                 launch_failed=True,
1289:             )
1290:             _append_log(
1291:                 custody_root,
1292:                 "dead-man found no live process-group identity in chain.started",
1293:             )
1294:         else:
1295:             group_alive = True
1296:             try:
1297:                 os.killpg(pgid, 0)
1298:             except ProcessLookupError:
1299:                 group_alive = False
1300:             except PermissionError:
1301:                 group_alive = True
1302:             if group_alive:
1303:                 _write_driver_refusal(
1304:                     night_dir / "refusal.json",
1305:                     plan,
1306:                     _CODES["chain_alive"],
1307:                     "chain process group is still alive or cannot be disproven",
1308:                     {"pgid": pgid},
1309:                 )
1310:                 _append_log(custody_root, "dead-man refused while chain was alive")
1311:                 _durable_record(custody_root, night_dir, plan)
1312:                 return EXIT_REFUSED
1313:             _record_chain_exit(night_dir, None, reaped_by="dead-man")
1314:             _append_log(custody_root, "dead-man proved the chain process group was gone")
1315: 
1316:     probes = make_probes()
1317:     probe, census_refusal = agent_census(probes)
1318:     _append_census(night_dir / "censuses.jsonl", probe, census_refusal)
1319:     if census_refusal is not None and not (night_dir / "refusal.json").exists():
1320:         refusal = _refusal_from_object(census_refusal) or {}
1321:         _write_driver_refusal(
1322:             night_dir / "refusal.json",
1323:             plan,
1324:             str(refusal.get("reason")),
1325:             str(refusal.get("detail")),
1326:             refusal.get("evidence"),
1327:         )
1328:     _append_log(custody_root, "dead-man starting courier")
1329:     _durable_record(custody_root, night_dir, plan)
1330:     if resolved_courier is None:
1331:         outcome = {
1332:             "attempted": 0,
1333:             "sent": False,
1334:             "heartbeat_seen": False,
1335:             "last_error": courier_error,
1336:         }
1337:     else:
1338:         outcome = run_courier(custody_root, plan, resolved_courier)
1339:     if not (night_dir / "courier.json").exists():
1340:         _write_courier_outcome(night_dir, outcome)
1341:     _durable_record(custody_root, night_dir, plan)
1342:     return EXIT_GO if outcome["sent"] else EXIT_COURIER_FAILED
1343: 
1344: 
1345: def build_parser() -> argparse.ArgumentParser:
1346:     parser = argparse.ArgumentParser(
1347:         description=__doc__,
1348:         epilog=(
1349:             "Exit 0: GO chain/courier succeeded; 3: refusal; 4: census abort; "
1350:             "5: chain failure; 6: courier failure."
1351:         ),
1352:     )
1353:     subcommands = parser.add_subparsers(dest="command", required=True)
1354:     for name in ("run", "dead-man", "rehearse"):
1355:         command = subcommands.add_parser(name)
1356:         command.add_argument("--plan", required=True, type=Path, metavar="PLAN.json")
1357:         command.add_argument("--courier-bin", type=Path, metavar="ABSOLUTE_PATH")
1358:     return parser
1359: 
1360: 
```

### 4d. launchd plist template (both fire times)
```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.joulewise.night</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/env</string>
    <string>python3</string>
    <string>@@REPO@@/scripts/run_night.py</string>
    <string>@@MODE@@</string>
    <string>--plan</string>
    <string>@@PLAN@@</string>
    <string>--courier-bin</string>
    <string>@@COURIER_BIN@@</string>
  </array>
  <key>WorkingDirectory</key>
  <string>@@REPO@@</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>@@PATH@@</string>
  </dict>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>@@HOUR@@</integer>
    <key>Minute</key>
    <integer>@@MINUTE@@</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>@@CUSTODY_ROOT@@/night/@@LOG_STEM@@.out</string>
  <key>StandardErrorPath</key>
  <string>@@CUSTODY_ROOT@@/night/@@LOG_STEM@@.err</string>
  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>
```

## 5. Why this packet exists (trigger record)

- Fix round 3 cured terra F3 (§2) by making the dead-man treat an EMPTY or
  null-pgid `chain.started` as a failed launch (courier, never `killpg`).
- Luna 132 (§1) rules that cure introduces D1: the marker is created empty by
  the O_EXCL claim BEFORE `Popen`, so a dead-man that runs during that window
  reads "launch failed" for a chain that is actually starting.
- Both findings are about the same thing — what an incomplete
  `chain.started` MEANS to the dead-man — so a fix round 4 would be the
  second fix round on the same defect. Doctrine (CLAUDE.local.md rule 11)
  makes the cold gate MANDATORY here, and the standing escalation trigger
  says the next spend is a consult, not round three. This packet is that
  consult.
- Both launchd jobs fire by `StartCalendarInterval` (§4d): the run job at the
  plan's armed hour, the dead-man at `DEADMAN_HOUR:DEADMAN_MINUTE` (07:00).
  The run path refuses `night_plan_overruns_deadman` unless
  `t0 + window_max_s + COURIER_DEADLINE_S < _next_deadman_epoch(t0)` (§4b).

## 6. Questions for the seat (answer each; cite line numbers)

Q1. Is D1 REACHABLE on the armed machine? Enumerate every schedule under
    which the dead-man process executes lines 1279-1314 while the run
    process is between the O_EXCL `open` (line ~352) and
    `_complete_chain_start` (line ~360-371). Include: launchd firing both
    jobs in the same second (armed hour == 07:00 or a run job whose plan sets
    t0 ≥ 07:00 — say what §4b does with that), a run job delayed by launchd
    (machine asleep, "missed" StartCalendarInterval fires coalesced on wake),
    and a manual `run` invocation at 07:00. For each: REACHABLE / NOT
    REACHABLE with the line that prevents it.
Q2. If reachable under ANY schedule, what is the smallest change that makes
    the dead-man's reading of `chain.started` unambiguous? Candidates the
    seat must rank (or beat): (a) claim with a SEPARATE O_EXCL file
    (`chain.claim`) and write `chain.started` only as a complete document via
    temp+rename, so the dead-man sees either no marker or a complete one;
    (b) keep the single marker but give the dead-man a launch grace
    (`LAUNCH_GRACE_S`) keyed on the marker's mtime: an empty/partial marker
    younger than the grace is re-read until complete or the grace expires;
    (c) the dead-man refuses `night_chain_alive` on an empty marker (round-2
    behaviour) AND the run path itself writes `chain.exited` on Popen failure
    (round-3 F3 cure), i.e. drop only the dead-man's null branch; (d) other.
    Rank by: does it close D1 fully; does it reopen F3; does it add a new
    state the courier prompt or `night_gate` schema must learn; test cost.
Q3. Does the chosen change keep every R-7 property in §3 — exactly one
    courier per night, dead-man never couriers while the chain is alive,
    dead-man never `killpg`s a null pgid, durable record before courier?
Q4. Luna's residual: `dead_man()` has no explicit pre-`t0` guard. Is that a
    defect under R-7 (a dead-man that fires BEFORE the night's t0 — e.g. a
    plan armed for 23:00 with the dead-man at 07:00 the same calendar day
    that the LaunchAgent was installed)? State what the dead-man does today
    on a night dir with NO `chain.started` (line numbers), and whether that
    is the right behaviour.

## 7. Report shape

Verdict first: `RULING` with Q1 table, Q2 ranked choice with the one-line
reason per rejected candidate, Q3 yes/no per property, Q4 finding.
Then dissent (anything the seat would have ruled differently from R-7 itself).
Under 90 lines. No code edits; no chain, `claude`, `launchctl`, or `git push`.
