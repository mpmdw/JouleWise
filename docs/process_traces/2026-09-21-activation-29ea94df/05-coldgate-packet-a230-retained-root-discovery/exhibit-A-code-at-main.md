# Exhibit A — code at main `9e0a4995`: the tracked check's retention classifier, its caller, the watchdog's span rules, the installer's terminal record set

## A1 `joulewise/evidence_night.py` lines 657–669 (`git show 9e0a4995:joulewise/evidence_night.py | sed -n 657,669p`)
```python
def retained_roots(state):
    inventory = []
    for plan in sorted((safe_path(state["roots_under"]) / "night-custody").glob("*/night_plan.json")):
        safe_path(plan)
        if not plan.is_file():
            raise Refused("retained plan is not a regular non-symlink file: " + str(plan))
        markers = [p for p in (plan.parent / "night/courier.sent", plan.parent / "night/result.json")
                   if safe_path(p).is_file()]
        inventory.append(dict(plan=str(plan), classification="retained" if markers else "UNKNOWN",
                              evidence=[str(p) for p in markers]))
    return dict(inventory=inventory, verdict="fail" if any(
        row["classification"] == "UNKNOWN" for row in inventory) else "pass")

```

## A2 `joulewise/evidence_night.py` lines 828–846 (the check driver that calls it)
```python
                raise Refused("exclusive install close has passed")
            return dict(digests=state["digests"], schedule=s)

        if inspect("sealed", seal):
            inspect("night_agents", lambda: require_no_night_agents(night_agents(state, launchctl_bin)))
            inspect("canonical", lambda: canonical_check(state, safe_path(canonical), runner))
            inspect("supervisor", lambda: supervisor_check(state, safe_path(canonical), supervisor_state, runner))
            courier = shutil.which("claude")
            checks["courier"] = dict(verdict="pass" if courier else "fail", path=courier,
                                      reason="courier on PATH" if courier else "courier unavailable")
            inspect("retained_roots", lambda: retained_roots(state))
            inspect("census", lambda: census_check(state, runner, census_observer,
                                                   os.getpid() if caller_pid is None else caller_pid))
            inspect("retry", lambda: retry_inventory(state, Path(candidate)))
        passed = all(c["verdict"] == "pass" for c in checks.values())
        record["armable"] = passed and not record["fake_launchctl"]
        record["rehearsal_ready"] = passed and record["fake_launchctl"]
        record["finished_epoch_s"] = time.time()
        path = lifecycle_dir(candidate) / "check.json"
```

## A3 `scripts/magistrate_watchdog.py` lines 770–800 (`plan_span_active`, `plan_is_armed`)
```python

def plan_completion_epoch(plan: NightPlan) -> float:
    return plan.t0_epoch_s + plan.window_max_s + COURIER_DEADLINE_S


def plan_span_active(plan: NightPlan, now_epoch_s: float, storage: Storage) -> bool:
    """File 15 row 3, including completion, courier, dead-man, and chain rules."""

    if now_epoch_s < plan.t0_epoch_s - PLAN_LEAD_S:
        return False
    night = Path(plan.custody_root) / "night"
    chain_open = storage.exists(night / "chain.started") and not storage.exists(
        night / "chain.exited"
    )
    if chain_open:
        return True
    if now_epoch_s <= plan_completion_epoch(plan):
        return True
    if storage.exists(night / "courier.sent"):
        return False
    return now_epoch_s <= deadman_epoch(plan) + COURIER_LOCK_FRESH_S


def plan_is_armed(plan: NightPlan, now_epoch_s: float, storage: Storage) -> bool:
    """An authored plan remains armed until its durable completion or final bound."""

    if plan.authored_epoch_s > now_epoch_s:
        return False
    night = Path(plan.custody_root) / "night"
    if storage.exists(night / "chain.started") and not storage.exists(night / "chain.exited"):
        return True
```

## A4 `joulewise/night_agent_install.py` lines 1129–1145 (the installer's set of night records that refuse admission)
```python
                        getattr(args, "probe_timeout_s", 600))
    # Every refusal document the driver would report from its existence alone
    # (run_night._refusal_paths: refusal.json, refusal-N.json,
    # calibration-refusal.json and its .*.json siblings) refuses admission like
    # any other night record (refuter 10 F1; fresh eyes 17 F2).
    records = [name for name in ("receipt.json", "result.json", "chain.started",
               "chain.exited", "courier.json", "courier.sent")
               if os.path.lexists(prepared.custody_night / name)]
    if prepared.custody_night.is_dir():
        records += [path.name for path in run_night._refusal_paths(prepared.custody_night)]
    records = sorted(set(records))
    if records:
        raise Refused(3, "refusing install: existing night records: " + " ".join(records))
    # All read-only refusals precede admission and mkdir.
    prepared.admit(time.time(), require_published=args.render_only is None)
    for field in ("hour", "minute"):
        supplied = getattr(args, field, None)
```

## A5 `scripts/run_night.py` lines 280–285 (`_refusal_paths`)
```python

def _refusal_paths(night_dir: Path) -> list[Path]:
    return sorted({*night_dir.glob("refusal.json"), *night_dir.glob("refusal-[0-9]*.json"),
                   *night_dir.glob("calibration-refusal.json"),
                   *night_dir.glob("calibration-refusal.json.*.json")})

```

## A6 `tests/test_evidence_night.py` lines 719–730 and 1251–1258 (the existing regressions)
```python
    def test_discovery_retains_every_harvested_root_and_refuses_unknown(self):
        for i, marker in enumerate(("courier.sent", "result.json", None)):
            root = self.custody.parent / f"prior-{i}"
            (root / "night").mkdir(parents=True)
            (root / "night_plan.json").write_text("{}")
            if marker:
                (root / "night" / marker).write_text("{}")
        result = self.checked("retained_roots")["checks"]["retained_roots"]
        self.assertEqual([r["classification"] for r in result["inventory"]], ["retained", "retained", "UNKNOWN"])
        self.assertTrue((root / "night_plan.json").exists())
        (root / "night/result.json").write_text("{}")
        self.assertTrue(self.checked()["rehearsal_ready"])
# ...
    def test_b12_retained_plan_must_be_regular(self):
        root = self.custody.parent / "retained"
        (root / "night").mkdir(parents=True)
        (root / "night/result.json").write_text("{}")
        (root / "night_plan.json").mkdir()
        with self.assertRaisesRegex(entry.Refused, "retained_roots"):
            entry.check(**self.kw)
        self.assertTrue((root / "night_plan.json").is_dir())
```

## A7 `joulewise/arm_census.py` lines 206–240 (`classify_arm_census`: how own, exempt and foreign PIDs are derived)
```python
def classify_arm_census(plan: NightPlan, observation: Observation, *, caller_pid: int) -> Verdict:
    """Classify one observation without process reads, effects or night policy."""
    own = _ancestors(observation.inventory, caller_pid)
    records = {row.pid: row for row in observation.records}
    relevant = set().union(*(
        _ancestors(observation.inventory, pid) for pid in observation.hit_pids
    )) if observation.hit_pids else set()
    roots = {pid for pid in relevant if pid in records and _interactive_root(records[pid])}
    # Exact ancestry finds roots even when discovery omits them; an unreadable
    # own-chain discovery hit still anchors descendant workload scanning.
    own_root = _own_root(observation.inventory, records, caller_pid, set(observation.hit_pids))
    if own_root is not None:
        roots.add(own_root)
    workloads: dict[int, str] = {}
    sessions = []
    exempt = set(own)
    for pid in sorted(roots):
        descendants = observation.inventory.descendants(pid)
        work = tuple(
            (child, category)
            for child in sorted(descendants - own)
            if child in records and (category := _workload(records[child])) is not None
        )
        workloads.update(work)
        idle_exemption = plan.receipt_class == "REHEARSAL_STUB" and not work and (
            pid in own or (pid in records and _interactive_root(records[pid]))
        )
        if idle_exemption:
            exempt.update(descendants | {pid})
        sessions.append(Session(pid, tuple(sorted(descendants)), work, idle_exemption))
    # Missing/unreadable exact records are unknown, hence idle, with diagnostics.
    foreign = (set(observation.hit_pids) & records.keys()) - exempt
    return Verdict(plan.receipt_class, tuple(sorted(own)), tuple(sessions),
                   tuple(sorted(foreign)), tuple(sorted(workloads.items())), observation.diagnostics)

```

## A8 `joulewise/evidence_night.py`: the census check that consumes that verdict (`grep -n` for the refusal sites, then the function body)
```python
65:        raise Refused(f"existing foreign or uncheckpointed output: {path}")
697:def census_check(state, runner, observer, caller_pid):
712:        resolved = set(verdict["own_pids"]) | set(verdict["foreign_pids"])
722:                    verdict["foreign_pids"] or verdict["diagnostics"] or verdict["workloads"] or reason) else "fail",
725:                instruction="Magistrate, all owned agents, MCP children and helpers must be gone before REQUEST.")
1256:                        record["recovery"] = "foreign_jobs_preserved"
# --- body:
def census_check(state, runner, observer, caller_pid):
    argv = clone_census(state, caller_pid, argv_only=True)["argv"]
    raw = runner(argv)
    raw_pids = set()
    if raw.returncode == 0:
        for line in raw.stdout.splitlines():
            match = re.match(r"^\s*([0-9]+)(?:\s|$)", line)
            if not match:
                raise Refused("unresolved raw census row: " + line)
            raw_pids.add(int(match[1]))
    observations = []
    for _ in range(2):
        result = clone_census(state, caller_pid, observer(caller_pid=caller_pid) if observer else None)
        observations.append(result)
        verdict, observed = result["classification"], result["observation"]
        resolved = set(verdict["own_pids"]) | set(verdict["foreign_pids"])
        resolved.update(pid for pid, _ in verdict["workloads"])
        unknown = set(observed["hit_pids"]) - {r["pid"] for r in observed["records"]}
        unresolved = raw_pids - resolved - unknown
        if not unresolved:
            break
    reason = f"unresolved raw census hit pid {min(unresolved)}" if unresolved else None
    if unknown and not reason:
        reason = "unknown census hit pid " + str(min(unknown))
    return dict(verdict="pass" if raw.returncode in (0, 1) and not (
                    verdict["foreign_pids"] or verdict["diagnostics"] or verdict["workloads"] or reason) else "fail",
                reason=reason, argv=argv, raw=observation_record(raw), observations=observations,
                classification=verdict, observation=observed, owned_helpers=verdict["own_pids"],
                instruction="Magistrate, all owned agents, MCP children and helpers must be gone before REQUEST.")


def night_agents(state, launchctl_bin):
    code = """import json,os,subprocess,sys
from pathlib import Path
from joulewise.night_agent_install import Target, LaunchctlAdapter, LABELS
directory=Path.home()/'Library/LaunchAgents'
target=Target.for_mode(directory)
listing=subprocess.run([sys.argv[1],'list'],capture_output=True,text=True)
labels=set(LABELS)
labels.update(line.split()[-1] for line in listing.stdout.splitlines()
              if line.split() and line.split()[-1].startswith(LABELS[0]))
```

## A9 `docs/contracts/evidence_night_entry.md` lines 213–226 (check item 5, the census)
```
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
```
