# Exhibit A — code at main `91f80870`

Every block below is the verbatim output of `git show 91f80870:<path>`, located by `ast` (function/class/assignment spans) or by exact text match, printed with 1-based line numbers. Nothing is read from the working tree.

## A1 — `joulewise/night_gate.py`: load predicate, reason codes, decision-record fields, `_check_machine`, hard-gate call site

### A1a load probe constant `LOAD_AVG_ARGV` — `joulewise/night_gate.py:148-148`

```python
  148  LOAD_AVG_ARGV = ("/usr/sbin/sysctl", "-n", "vm.loadavg")
```

### A1b load ceiling `LOAD_MAX` — `joulewise/night_gate.py:152-152`

```python
  152  LOAD_MAX = 2.0
```

### A1c constants block in context (agent census argv through LOAD_MAX) — `joulewise/night_gate.py:137-154`

```python
  137  AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-lf", "[c]odex|[c]laude|[t]3")
  138  
  139  PMSET_BATT_ARGV = ("/usr/bin/pmset", "-g", "batt")
  140  PMSET_GENERAL_ARGV = ("/usr/bin/pmset", "-g")
  141  HID_IDLE_ARGV = (
  142      "/usr/bin/defaults",
  143      "-currentHost",
  144      "read",
  145      "com.apple.screensaver",
  146      "idleTime",
  147  )
  148  LOAD_AVG_ARGV = ("/usr/sbin/sysctl", "-n", "vm.loadavg")
  149  THERMAL_ARGV = ("/usr/bin/pmset", "-g", "therm")
  150  BOOT_SESSION_ARGV = ("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid")
  151  
  152  LOAD_MAX = 2.0
  153  PLAN_MAX_AGE_S = 36 * 60 * 60
  154  
```

### A1d gate reason codes `NIGHT_GATE_REASON_CODES` — `joulewise/night_gate.py:155-173`

```python
  155  NIGHT_GATE_REASON_CODES = frozenset(
  156      {
  157          "night_refused_agent_present",
  158          "night_refused_not_quiet",
  159          "night_refused_bind_expired",
  160          "night_refused_hid_idle",
  161          "night_refused_boot_clock",
  162          "night_refused_registration",
  163          "night_window_expired",
  164          "night_plan_stale",
  165          "night_plan_malformed",
  166          "night_chain_digest_mismatch",
  167          "launch_go_receipt_missing",
  168          "launch_go_receipt_invalid",
  169          "night_refused_class_unbuilt",
  170          "night_receipt_class_invalid",
  171          "night_probe_error",
  172      }
  173  )
```

### A1e decision-record field set (contains `top_consumers_at_decision`, `load_avg_diagnostic`) `_QUIET_RECEIPT_KEYS` — `joulewise/night_gate.py:242-247`

```python
  242  _QUIET_RECEIPT_KEYS = {
  243      "quiet_admission", "bind_deadline_epoch_s", "go_epoch_s", "samples_total",
  244      "samples_quiet_run_at_go", "quiet_samples_sha256", "quiet_samples_lines",
  245      "top_consumers_at_decision", "load_avg_diagnostic",
  246      "admission_is_capture_evidence",
  247  }
```

### A1f `_check_machine` — `joulewise/night_gate.py:1262-1391`

```python
 1262  def _check_machine(plan, probes, rows, evidence, *, legacy_load=True):
 1263      # R-6's unattended HID predicate precedes the remaining quiet predicates.
 1264      try:
 1265          hid = _run(probes, HID_IDLE_ARGV)
 1266      except ProbeError as exc:
 1267          return _probe_refusal(plan, probes, rows, evidence, exc)
 1268      evidence.append(hid)
 1269      rows["C3"].evidence.append(_probe_citation(hid))
 1270      rows["C3"].measured["hid_idle_raw"] = hid.stdout
 1271      if not legacy_load and not _completed_ok(hid):
 1272          return _probe_refusal(plan, probes, rows, evidence, ProbeError("screensaver probe failed"))
 1273      if not legacy_load and not re.fullmatch(r"[0-9]+", hid.stdout.strip()):
 1274          return _probe_refusal(plan, probes, rows, evidence, ProbeError("screensaver output malformed"))
 1275      if not _completed_ok(hid) or hid.stdout.strip() != "0":
 1276          return _finish(
 1277              plan,
 1278              probes,
 1279              rows,
 1280              Refusal(
 1281                  "night_refused_hid_idle",
 1282                  f"screensaver idleTime must be exactly 0 (exit={hid.exit_code}, stdout={hid.stdout.strip()!r})",
 1283                  tuple(evidence),
 1284              ),
 1285          )
 1286  
 1287      # R-11 quiet predicates, in a fixed and reviewable command order.
 1288      try:
 1289          batt = _run(probes, PMSET_BATT_ARGV)
 1290          evidence.append(batt)
 1291          rows["C3"].evidence.append(_probe_citation(batt))
 1292          rows["C3"].measured["ac_power_raw"] = batt.stdout
 1293          if not legacy_load and (not _completed_ok(batt) or not any(
 1294                  power in batt.stdout for power in ("AC Power", "Battery Power"))):
 1295              raise ProbeError("power observation malformed or failed")
 1296          if not _completed_ok(batt) or "AC Power" not in batt.stdout:
 1297              return _finish(
 1298                  plan,
 1299                  probes,
 1300                  rows,
 1301                  Refusal(
 1302                      "night_refused_not_quiet",
 1303                      "ac_power",
 1304                      tuple(evidence),
 1305                  ),
 1306              )
 1307  
 1308          settings = _run(probes, PMSET_GENERAL_ARGV)
 1309          evidence.append(settings)
 1310          rows["C3"].evidence.append(_probe_citation(settings))
 1311          rows["C3"].measured["pmset_g_raw"] = settings.stdout
 1312          display_match = _DISPLAY_SLEEP_RE.search(settings.stdout)
 1313          rows["C3"].measured["displaysleep"] = (
 1314              None if display_match is None else display_match.group(1)
 1315          )
 1316          if not legacy_load and (not _completed_ok(settings) or display_match is None):
 1317              raise ProbeError("display configuration observation malformed or failed")
 1318          if not _completed_ok(settings) or display_match is None:
 1319              return _finish(
 1320                  plan,
 1321                  probes,
 1322                  rows,
 1323                  Refusal(
 1324                      "night_refused_not_quiet",
 1325                      "displaysleep predicate failed",
 1326                      tuple(evidence),
 1327                  ),
 1328              )
 1329  
 1330          if legacy_load:
 1331              load = _run(probes, LOAD_AVG_ARGV)
 1332              evidence.append(load)
 1333              rows["C3"].evidence.append(_probe_citation(load))
 1334              rows["C3"].measured["load_average_raw"] = load.stdout
 1335              load_match = _LOAD_AVG_RE.fullmatch(load.stdout.strip())
 1336              if not _completed_ok(load) or load_match is None:
 1337                  raise ProbeError(
 1338                      "load average output malformed: "
 1339                      f"exit={load.exit_code}, stdout={load.stdout[:200]!r}"
 1340                  )
 1341              load_1m = float(load_match.group(1))
 1342              rows["C3"].measured["load_1m"] = load_1m
 1343              if load_1m > LOAD_MAX:
 1344                  return _finish(
 1345                      plan,
 1346                      probes,
 1347                      rows,
 1348                      Refusal(
 1349                          "night_refused_not_quiet",
 1350                          f"load_average predicate failed (maximum {LOAD_MAX})",
 1351                          tuple(evidence),
 1352                      ),
 1353                  )
 1354  
 1355          thermal = _run(probes, THERMAL_ARGV)
 1356          evidence.append(thermal)
 1357          rows["C3"].evidence.append(_probe_citation(thermal))
 1358          rows["C3"].measured["thermal_raw"] = thermal.stdout
 1359          thermal_limits: list[str] = []
 1360          for thermal_line in thermal.stdout.splitlines():
 1361              stripped_line = thermal_line.strip()
 1362              if not stripped_line.startswith("CPU_Speed_Limit"):
 1363                  continue
 1364              thermal_match = _THERMAL_RE.fullmatch(stripped_line)
 1365              if thermal_match is None:
 1366                  raise ProbeError(
 1367                      f"thermal output malformed: {thermal.stdout[:200]!r}"
 1368                  )
 1369              thermal_limits.append(thermal_match.group(1))
 1370          thermal_limit = thermal_limits[0] if thermal_limits else None
 1371          rows["C3"].measured["cpu_speed_limit"] = thermal_limit
 1372          if not _completed_ok(thermal):
 1373              raise ProbeError(
 1374                  f"thermal probe exit {thermal.exit_code}: {thermal.stdout[:200]!r}"
 1375              )
 1376          if any(limit != "100" for limit in thermal_limits):
 1377              return _finish(
 1378                  plan,
 1379                  probes,
 1380                  rows,
 1381                  Refusal(
 1382                      "night_refused_not_quiet",
 1383                      "thermal predicate failed",
 1384                      tuple(evidence),
 1385                  ),
 1386              )
 1387      except ProbeError as exc:
 1388          return _probe_refusal(plan, probes, rows, evidence, exc)
 1389      rows["C3"].status = "PASS"
 1390      rows["C3"].measured["detail"] = ("agent, HID, AC, display, load, and thermal predicates passed"
 1391          if legacy_load else "agent, screensaver configuration, AC, display and thermal predicates passed")
```

_A1g hard-gate call site: hit at line 1530; enclosing function `evaluate_dynamic_hard`._

### A1g hard-gate call site (hit line 1530, enclosing `evaluate_dynamic_hard`) — `joulewise/night_gate.py:1522-1536`

```python
 1522  def evaluate_dynamic_hard(plan: NightPlan, probes: Probes, static: Receipt) -> Receipt:
 1523      """Re-observe every hard predicate; CPU admission belongs to the driver."""
 1524      rows = {row.condition_id: _MutableCondition(row.status, row.basis, list(row.evidence),
 1525                                                 dict(row.measured)) for row in static.conditions}
 1526      evidence = []
 1527      refused = _check_census(plan, probes, rows, evidence, strict=True)
 1528      if refused is not None:
 1529          return refused
 1530      refused = _check_machine(plan, probes, rows, evidence, legacy_load=False)
 1531      if refused is not None:
 1532          return refused
 1533      refused = _check_clock(plan, probes, rows, evidence, strict_probe=True)
 1534      if refused is not None:
 1535          return refused
 1536      return replace(_finish(plan, probes, rows, None,
```

## A2 — `joulewise/quiet_admission.py`: the driver-side quiet predicate

### A2a `is_quiet` — `joulewise/quiet_admission.py:165-170`

```python
  165  def is_quiet(metrics, policy):
  166      busy = metrics["busy_cores"]
  167      if isinstance(busy, bool) or not isinstance(busy, (int, float)) or not math.isfinite(busy) or busy < 0:
  168          raise ValueError("invalid busy_cores")
  169      # Zero is the explicitly non-admitting validation-fixture sentinel.
  170      return policy["busy_core_max"] > 0 and busy <= policy["busy_core_max"]
```

### A2b `validate_policy` — `joulewise/quiet_admission.py:38-58`

```python
   38  def validate_policy(value, *, window_max_s=None):
   39      if not isinstance(value, Mapping) or set(value) != POLICY_KEYS:
   40          raise ValueError("quiet_admission must have exactly all seven policy keys")
   41      if value["policy_id"] != "cpu_interval_v1":
   42          raise ValueError("unknown quiet_admission policy_id")
   43      if not isinstance(value["cutoff_authority"], str) or not value["cutoff_authority"].strip():
   44          raise ValueError("cutoff_authority must name a non-empty cutoff ruling record path")
   45      for key in POLICY_KEYS - {"policy_id", "cutoff_authority"}:
   46          number = value[key]
   47          if (isinstance(number, bool) or not isinstance(number, (int, float))
   48                  or not math.isfinite(number) or number < 0
   49                  or (number == 0 and key != "busy_core_max")):
   50              raise ValueError(f"quiet_admission.{key} must be finite and positive (cutoff may be zero)")
   51      top_argv(value["sample_interval_s"])
   52      if type(value["consecutive_quiet_samples"]) is not int:
   53          raise ValueError("consecutive_quiet_samples must be an integer >= 1")
   54      if value["bind_max_s"] < value["sample_interval_s"] * value["consecutive_quiet_samples"]:
   55          raise ValueError("bind_max_s cannot hold the consecutive quiet samples")
   56      if window_max_s is not None and window_max_s < value["bind_max_s"] + value["post_bind_budget_s"]:
   57          raise ValueError("window_max_s must hold bind_max_s + post_bind_budget_s")
   58      return dict(value)
```

_A2c top_consumers builder: hit at line 162; enclosing function `interval_metrics` (lines 122-162), shown whole._

### A2c top_consumers builder `interval_metrics` — `joulewise/quiet_admission.py:122-162`

```python
  122  def interval_metrics(before, after, *, interval_s, idle_fraction, logical_cpu,
  123                       observer_pid, wall_start, last_seen=None):
  124      """Account for the union of identities; last_seen may include exit evidence.
  125  
  126      Without a measurable exit counter, list the process as unaccounted. Host
  127      busy time still counts that work. New processes count their lifetime CPU
  128      only when their start identity places them within this interval.
  129      """
  130      if (not math.isfinite(interval_s) or interval_s <= 0
  131              or not math.isfinite(idle_fraction) or not 0 <= idle_fraction <= 1
  132              or type(logical_cpu) is not int or logical_cpu <= 0):
  133          raise ValueError("invalid interval/host observation")
  134      last_seen = last_seen or {}
  135      all_rows = {**before, **last_seen, **after}
  136      observers = {observer_pid}
  137      while True:
  138          extended = observers | {row["pid"] for row in all_rows.values() if row["ppid"] in observers}
  139          if extended == observers:
  140              break
  141          observers = extended
  142      consumers, unaccounted = [], []
  143      for identity in sorted(set(before) | set(after) | set(last_seen)):
  144          first = before.get(identity)
  145          final = after.get(identity, last_seen.get(identity))
  146          row = final or first
  147          if final is None or (first is None and row["start_epoch_s"] < wall_start):
  148              unaccounted.append(dict(pid=row["pid"], start_identity=row["start_identity"],
  149                                      command=row["command"], reason="no measurable interval delta"))
  150              continue
  151          delta = final["cumulative_cpu_seconds"] - (first["cumulative_cpu_seconds"] if first else 0)
  152          if not math.isfinite(delta) or delta < 0:
  153              raise ValueError("CPU counter regressed for the same process identity")
  154          consumers.append(dict(pid=row["pid"], start_identity=row["start_identity"],
  155                                command=row["command"], busy_cores=delta / interval_s,
  156                                observer=row["pid"] in observers))
  157      process_busy = sum(item["busy_cores"] for item in consumers)
  158      host_busy = logical_cpu * (1 - idle_fraction)
  159      return dict(process_busy_cores=process_busy, host_busy_cores=host_busy,
  160                  busy_cores=max(process_busy, host_busy), logical_cpu=logical_cpu,
  161                  idle_fraction=idle_fraction, unaccounted=unaccounted,
  162                  top_consumers=sorted(consumers, key=lambda item: (-item["busy_cores"], item["pid"]))[:10])
```

## A3 — `joulewise/quiet_predicate_campaign.py`: covariates, stop branch, sizing, pilot summary, attestation exclusions

### A3a `record_covariates` — `joulewise/quiet_predicate_campaign.py:841-860`

```python
  841  def record_covariates(protocol, night_dir):
  842      from joulewise.quiet_admission import sample_interval
  843      from scripts.sample_quiet_predicate_evidence import cpu_total
  844      stop = False
  845      def stopping(_signum, _frame):
  846          nonlocal stop
  847          stop = True
  848      signal.signal(signal.SIGTERM, stopping)
  849      journal = night_dir / protocol["recorder_journal"]
  850      while not stop:
  851          cpu, began = cpu_total(), time.monotonic()
  852          try:
  853              value = sample_interval(protocol["sample_interval_s"])
  854              row = {"observation": value, "error": None}
  855          except (OSError, ValueError, subprocess.SubprocessError) as exc:
  856              row = {"observation": None, "error": str(exc)}
  857          row.update(evidence_status="PROVISIONAL", role="covariate_only", admits_nothing=True,
  858                     observer_cpu_s=cpu_total() - cpu, monotonic_start=began, monotonic_end=time.monotonic())
  859          append_event(journal, row)
  860      return 0
```

### A3b `stop_branch` — `joulewise/quiet_predicate_campaign.py:925-940`

```python
  925  def stop_branch(*, s_upper=None, observer_floor=None, block_two_upper_j=None, protocol=None):
  926      """Apply only ruled stop conditions; absent evidence is never a pass."""
  927      protocol = frozen_protocol() if protocol is None else protocol
  928      smallest_share = protocol["block_two"]["smallest_holdable_share"]
  929      for value in (s_upper, observer_floor, smallest_share, block_two_upper_j):
  930          if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
  931              raise ValueError("stop-branch evidence must be finite and nonnegative")
  932      causes = []
  933      pairs = None if s_upper is None else size_block_two(s_upper, protocol)
  934      if pairs is not None and pairs > protocol["sizing"]["maximum_pairs"]:
  935          causes.append("sized_pairs_above_24")
  936      if observer_floor is not None and observer_floor > smallest_share:
  937          causes.append("observer_floor_above_smallest_holdable_share")
  938      if block_two_upper_j is not None and block_two_upper_j > protocol["sizing"]["delta_j"]:
  939          causes.append("block_two_upper_bound_above_1_J")
  940      return {"outcome": protocol["stop_branches"][causes[0]] if causes else "no decision", "causes": causes, "pairs": pairs}
```

### A3c `size_block_two` — `joulewise/quiet_predicate_campaign.py:918-922`

```python
  918  def size_block_two(s_upper, protocol=None):
  919      if type(s_upper) not in (float, int) or not math.isfinite(s_upper) or s_upper < 0:
  920          raise ValueError("s_upper must be a finite nonnegative upper confidence bound")
  921      sizing = (frozen_protocol() if protocol is None else protocol)["sizing"]
  922      return max(sizing["minimum_pairs"], math.ceil(sizing["multiplier"] * s_upper ** 2 / sizing["delta_j"] ** 2))
```

### A3d `pilot_summary` — `joulewise/quiet_predicate_campaign.py:943-1162`

```python
  943  def pilot_summary(directory, protocol, envelopes, observer_cpu_s=None):
  944      """Apply ruling 46b to fixed pairs; preserve unfiltered diagnostics."""
  945      import statistics
  946      from scripts import sample_quiet_predicate_evidence as harness
  947      values, all_rows, replay_recorders = [], [], []
  948      journal = directory.parent / protocol["recorder_journal"]
  949      covariates = [json.loads(line) for line in journal.read_text().splitlines() if line] if journal.exists() else []
  950      clean_busy = []
  951      for entry in envelopes:
  952          excluded = []
  953          if entry.get("collector_exit", 0) != 0:
  954              excluded.append("collect_error")
  955          if entry.get("cleanup", {}).get("cleanup_proven") is False:
  956              excluded.append("cleanup_unproven")
  957          scheduled = entry.get("scheduled_mono_s")
  958          support = [r for r in covariates if scheduled is not None and
  959                     r["monotonic_start"] >= scheduled and
  960                     r["monotonic_end"] <= scheduled + protocol["envelope_s"]]
  961          busy = [(r.get("observation") or {}).get("metrics", {}).get("busy_cores") for r in support]
  962          distribution = harness.quantiles(busy)
  963          entry = {**entry, "busy_cores": {**distribution, "median": distribution["p50"]},
  964                   "busy_cores_samples": len([v for v in busy if harness.number(v) is not None]),
  965                   "recorder_observer_cpu_s": sum(r.get("observer_cpu_s") or 0 for r in support)}
  966          out = directory / f"envelope-{entry['index']:02d}"
  967          # The session record is read FIRST and kept even when the rest of the
  968          # envelope is unreadable, because the replay check below must see
  969          # every session that exists.  Reading both inside one `try` meant a
  970          # missing or unparseable `rounds.jsonl` skipped the envelope before
  971          # the check, and a replay night whose journals were all lost failed
  972          # OPEN -- INCONCLUSIVE, `partial`, rc 0 (execution lens 17b S1).
  973          session, rows, unreadable = None, None, None
  974          try:
  975              session = json.loads((out / "session.json").read_text())
  976              rows = [json.loads(line) for line in (out / "rounds.jsonl").read_text().splitlines() if line]
  977          except (OSError, ValueError) as exc:
  978              unreadable = exc
  979          # HARVEST-side fail-closed point of the bench replay (cold gate #3
  980          # ruling 10 Q7; brief D6).  Every session this summary reads must say,
  981          # in its own record, that a real `powermetrics` produced its frames.
  982          # An absent key is not a claim of production provenance either: the
  983          # bench replay writes "replay", and a session predating the key cannot
  984          # attest to anything, so both refuse.  The refusal is the SUMMARY's,
  985          # not an exclusion reason -- A269 byte-pins the registration's
  986          # exclusion list, and a new reason would force a registration v3.
  987          # `power: null` is NOT a contradicted claim of production provenance:
  988          # the collector initialises it to null and only fills it once a
  989          # recorder was BUILT, so a null is an envelope that refused before any
  990          # recorder existed -- the network-time provenance refusal path, which
  991          # excludes itself on its own terms.  Refusing a whole REAL night as a
  992          # "replay" because one envelope refused early is a false record, and
  993          # it was reachable (lane contract lens 17a S1).  Anything else -- a
  994          # power record that exists and does not say `powermetrics` -- refuses.
  995          power = session.get("power") if session is not None else None
  996          if session is not None and power is not None:
  997              recorder_kind = power.get("recorder_kind") if isinstance(power, dict) else None
  998              if recorder_kind != harness.RECORDER_KIND_PRODUCTION:
  999                  replay_recorders.append({"index": entry["index"], "recorder_kind": recorder_kind})
 1000          if unreadable is not None:
 1001              values.append({**entry, "excluded": excluded + ["incomplete_interior_support"],
 1002                             "error": str(unreadable), "joules": None})
 1003              continue
 1004          all_rows.extend(rows)
 1005          hard = hard_exclusions(rows)
 1006          excluded.extend(hard)
 1007          # Clock-discipline attestation (ruling 14 R4): only an envelope whose
 1008          # capture window carries no applied correction in the ``timed`` log is
 1009          # claim-bearing.  A slew inside the window and a failed or missing
 1010          # query are both HARD exclusions; the session record is authoritative
 1011          # and the executor's own envelope entry is the fallback, so a summary
 1012          # re-derived from disk reaches the same verdict.
 1013          #
 1014          # It is computed BEFORE the clean busy-core diagnostic below because
 1015          # that diagnostic describes the machine an envelope was captured on:
 1016          # an envelope whose clock was slewed, or whose discipline could not be
 1017          # attested at all, is not a clean-machine observation either, and
 1018          # feeding its covariates into the "clean" distribution would let an
 1019          # excluded envelope shape the number the paper reports.
 1020          provenance = session.get("network_time_provenance")
 1021          attestation = provenance.get("attestation") if isinstance(provenance, dict) else None
 1022          state = (attestation.get("state") if isinstance(attestation, dict)
 1023                   else entry.get("network_time_attestation"))
 1024          unattested = attestation_exclusions(state)
 1025          excluded.extend(unattested)
 1026          if not hard and not unattested:
 1027              clean_busy.extend(busy)
 1028          interior = session.get("interior", {})
 1029          if (session.get("power") or {}).get("anchor", {}).get("status") != "bounded":
 1030              excluded.append("clock_anchor_unresolved")
 1031          if not interior.get("complete_support"):
 1032              excluded.append("incomplete_interior_support")
 1033          entry = {**entry, "collector_start_drift_s": session.get("start_drift_s")}
 1034          if max(abs(entry["start_drift_s"]), abs(session.get("start_drift_s") or 0)) > protocol["start_drift_max_s"]:
 1035              excluded.append("start_drift")
 1036          if any(row.get("os_build_valid") is not True or row.get("os_build") != session.get("os_build") or
 1037                 row.get("session") != session.get("session") for row in rows):
 1038              raise ValueError("pilot row/session identity mismatch")
 1039          energy = (interior.get("power") or {}).get("energy_j", {})
 1040          values.append({**entry, "excluded": sorted(set(excluded)), "interior": interior,
 1041                         "joules": energy.get("rail_sum_w"), "combined_joules": energy.get("combined_w"),
 1042                         "boot_id": session.get("boot_id"), "os_build": session.get("os_build"),
 1043                         "sw_vers": session.get("sw_vers"), "powermetrics_identity": session.get("powermetrics_identity"),
 1044                         "whole_envelope_observer_cpu_s": session.get("whole_envelope_observer_cpu_s"),
 1045                         "observer_cpu_s": sum(row.get("observer_cpu_s") or 0 for row in rows),
 1046                         "censuses": [{"round": r["round"], "clean": r.get("census_clean")} for r in rows]})
 1047      retained = [v for v in values if not v["excluded"] and v["joules"] is not None]
 1048      # Index identity, not position in a filtered list, fixes the original pairs.
 1049      by_index = {v["index"]: v for v in values}
 1050      overlapping = []
 1051      for index in range(1, protocol["envelopes"]):
 1052          a, b = by_index.get(index), by_index.get(index + 1)
 1053          if a is None or b is None or a["joules"] is None or b["joules"] is None:
 1054              continue
 1055          overlapping.append({"left": index, "right": index + 1,
 1056              "delta_j": b["joules"] - a["joules"],
 1057              "retained": not a["excluded"] and not b["excluded"]
 1058                  and a.get("boot_id") == b.get("boot_id") and a.get("os_build") == b.get("os_build")})
 1059      deltas = [d for d in overlapping if d["retained"] and d["left"] % 2 == 1]
 1060      sufficient = len(retained) >= protocol["minimum_retained"] and len(deltas) >= protocol["minimum_adjacent_pairs"]
 1061      pair_sd = statistics.stdev(d["delta_j"] for d in deltas) if len(deltas) >= 2 else None
 1062      df = len(deltas) - 1 if len(deltas) >= 2 else None
 1063      factor = math.sqrt(df / chi_square_lower_decile(df)) if sufficient else None
 1064      s_upper = pair_sd * factor if sufficient else None
 1065      # Whole-round measured cost, including rejected envelopes; never subtract
 1066      # it from energy or use it as an envelope retention input.
 1067      observer_rows = [r for r in all_rows if harness.number(r.get("observer_cpu_s")) is not None
 1068                       and harness.number(r.get("round_mono_start_s")) is not None
 1069                       and harness.number(r.get("round_mono_end_s")) is not None
 1070                       and r["round_mono_end_s"] > r["round_mono_start_s"]]
 1071      observer_support_s = sum(r["round_mono_end_s"] - r["round_mono_start_s"] for r in observer_rows)
 1072      observer_floor = sum(r["observer_cpu_s"] for r in observer_rows) / observer_support_s if observer_support_s else None
 1073      stop = stop_branch(s_upper=s_upper, observer_floor=observer_floor, protocol=protocol)
 1074      unfiltered = [v["joules"] for v in values if v["joules"] is not None]
 1075      large_pairs = [d for d in overlapping if pair_sd is not None and abs(d["delta_j"]) > 3 * pair_sd]
 1076      report = {"schema": "joulewise.quiet_predicate_pilot_summary.v1", "evidence_status": "PROVISIONAL",
 1077          "status": "SPREAD_RECORDED" if sufficient else "INCONCLUSIVE", "envelopes": values,
 1078          "retained": len(retained), "sizing_pairs": deltas, "retained_pairs": len(deltas),
 1079          "adjacent_pairs": overlapping, "adjacent_pairs_role": "diagnostic_only; never used for sizing",
 1080          "adjacent_pair_sd_j": statistics.stdev(d["delta_j"] for d in overlapping) if len(overlapping) >= 2 else None,
 1081          "pair_sd_j": pair_sd, "pair_df": df, "s_upper_factor": factor,
 1082          "single_envelope_sd_j": statistics.stdev(v["joules"] for v in retained) if len(retained) >= 2 else None,
 1083          "unfiltered_single_envelope_sd_j": statistics.stdev(unfiltered) if len(unfiltered) >= 2 else None,
 1084          "single_envelope_role": "diagnostic_only; never used for sizing",
 1085          "first_to_last_retained_drift_j": retained[-1]["joules"] - retained[0]["joules"] if len(retained) >= 2 else None,
 1086          "pairs_above_3_pair_sd": large_pairs,
 1087          "pairs_above_3_pair_sd_role": "overlapping adjacent differences; diagnostic only",
 1088          "max_abs_delta_j": max((abs(d["delta_j"]) for d in overlapping), default=None),
 1089          "busy_cores": harness.quantiles(clean_busy), "busy_cores_role": "covariate_only; never excluded",
 1090          "busy_cores_source": protocol["recorder_journal"],
 1091          "busy_cores_support": "recorder intervals fully within each scheduled envelope",
 1092          "clean_machine_busy_cores": harness.quantiles(clean_busy),
 1093          "clean_machine_definition": "envelopes passing census, AC and thermal hard probes; independent of energy retention",
 1094          "observer_floor_cores": observer_floor, "observer_support_s": observer_support_s,
 1095          "s_upper": s_upper,
 1096          "s_upper_reason": "one-sided upper 90% chi-square bound; independent normal pair differences assumed"
 1097              if sufficient else "fewer than four retained disjoint pairs or eight retained envelopes; no top-up",
 1098          "block_two_pairs": stop["pairs"], "block_two_stop": stop,
 1099          "block_two_pairs_reason": "ruling 46b: " + protocol["sizing"]["formula"] +
 1100              f"; delta_j={protocol['sizing']['delta_j']}; stop above {protocol['sizing']['maximum_pairs']} pairs"
 1101              if sufficient else "INCONCLUSIVE; no sizing",
 1102          "whole_campaign_observer_cpu_s": observer_cpu_s,
 1103          "observer_definition": "SELF + reaped CHILDREN, including collector, recorder, sampler and census; never subtracted",
 1104          "cutoff_authority": False, "top_up": False}
 1105      if replay_recorders:
 1106          # Nothing this night produced is a measurement.  The status, the
 1107          # retained set and the spread bound are replaced outright rather than
 1108          # annotated -- and so is EVERY energy number the document would
 1109          # otherwise carry: the per-envelope joules and interiors, the sizing
 1110          # and adjacent pairs, and every spread or drift statistic derived
 1111          # from them (lane contract lens 17a N2 -- the claim below that no
 1112          # reader can lift a number was false while `sizing_pairs` and
 1113          # `envelopes[*].joules` survived the override).  What stays is the
 1114          # SCHEDULE side: index, scheduled and actual instants, start drift,
 1115          # collector exit, cleanup, attestation and busy-core covariates --
 1116          # the figures the bench replay exists to produce, none of which is an
 1117          # energy.
 1118          energy_blanked = [{**v, "joules": None, "combined_joules": None, "interior": None}
 1119                            for v in report["envelopes"]]
 1120          report.update({
 1121              "status": REPLAY_NEVER_EVIDENCE, "evidence_status": REPLAY_NEVER_EVIDENCE,
 1122              "retained": [], "s_upper": None,
 1123              "s_upper_reason": "replay recorder: no envelope of this night is a measurement",
 1124              "envelopes": energy_blanked,
 1125              "sizing_pairs": [], "retained_pairs": 0, "adjacent_pairs": [],
 1126              "adjacent_pair_sd_j": None, "pair_sd_j": None, "pair_df": None,
 1127              "s_upper_factor": None, "single_envelope_sd_j": None,
 1128              "unfiltered_single_envelope_sd_j": None,
 1129              "first_to_last_retained_drift_j": None, "pairs_above_3_pair_sd": [],
 1130              "max_abs_delta_j": None, "block_two_pairs": None, "block_two_stop": None,
 1131              "block_two_pairs_reason": "replay recorder: no sizing, no spread, no energy",
 1132              "replay_recorder_envelopes": replay_recorders,
 1133              "replay_recorder_reason": "one or more session.json records do not carry "
 1134                                        f"power.recorder_kind == {harness.RECORDER_KIND_PRODUCTION!r}"})
 1135      harness.write_json(directory / "summary.json", report)
 1136      if replay_recorders:
 1137          (directory / "summary.md").write_text(
 1138              f"# QPE-01 {REPLAY_NEVER_EVIDENCE}\n\n"
 1139              f"Status: {REPLAY_NEVER_EVIDENCE}. Envelopes "
 1140              f"{', '.join(str(r['index']) for r in replay_recorders)} were produced by a recorder "
 1141              f"that is not `powermetrics`, so this night is a BENCH REPLAY and none of it is a "
 1142              "measurement: no envelope is retained, no spread bound is computed, and the executor "
 1143              "refuses the night. Every energy number is blanked with it: no per-envelope "
 1144              "joules or interior, no sizing or adjacent pairs, no spread or drift statistic "
 1145              "derived from them. The per-envelope SCHEDULE, cleanup, attestation and "
 1146              "start-drift diagnostics in summary.json remain, because measuring the "
 1147              "inter-slot tail is what the replay is for.\n")
 1148          return report
 1149      (directory / "summary.md").write_text(
 1150          "# QPE-01 pilot (PROVISIONAL, descriptive)\n\n" +
 1151          f"Status: {report['status']}. Retained {len(retained)}/{protocol['envelopes']} envelopes; {len(deltas)} disjoint pairs.\n\n" +
 1152          f"Disjoint-pair sample SD: {pair_sd} J (df={df}); upper 90% bound: {s_upper} J. " +
 1153          "This chi-square construction assumes independent, normally distributed pair differences.\n\n" +
 1154          f"Block-two pairs: {stop['pairs']}; sizing stop: {stop['outcome']}. No sizing when INCONCLUSIVE.\n\n" +
 1155          f"Diagnostics only: {len(overlapping)} overlapping differences (SD {report['adjacent_pair_sd_j']} J); " +
 1156          f"single-envelope SD {report['unfiltered_single_envelope_sd_j']} J; " +
 1157          f"first-to-last retained drift {report['first_to_last_retained_drift_j']} J. " +
 1158          f"Overlapping adjacent pairs with |delta| > 3 * s_pair: {large_pairs}. Values are in summary.json.\n\n" +
 1159          "Busy cores are recorded covariates and never an exclusion input. " +
 1160          "Every exclusion and partial interior is retained in summary.json. No top-up, cutoff or activation authority. " +
 1161          "Block two is not authored by this summary.\n")
 1162      return report
```

### A3e `attestation_exclusions` — `joulewise/quiet_predicate_campaign.py:832-838`

```python
  832  def attestation_exclusions(state):
  833      """The ruled vocabulary: only an authenticated envelope is claim-bearing."""
  834      if state == "authenticated":
  835          return []
  836      if state == "slew_attested":
  837          return [NETWORK_TIME_SLEW_EXCLUSION]
  838      return [NETWORK_TIME_UNATTESTED_EXCLUSION]
```

### A3f `hard_exclusions` — `joulewise/quiet_predicate_campaign.py:863-885`

```python
  863  def hard_exclusions(rows):
  864      """Named mechanisms only. This function never reads busy-core values."""
  865      excluded = set()
  866      if not rows or any(row.get("census_clean") is not True for row in rows):
  867          excluded.add("census_not_clean_or_unknown")
  868      for row in rows:
  869          batches = row.get("hard_probes") or []
  870          probes = [probe for batch in batches for probe in batch.get("result", [])]
  871          ac = [p for p in probes if tuple(p.get("argv", [])) == night_gate.PMSET_BATT_ARGV]
  872          thermal = [p for p in probes if tuple(p.get("argv", [])) == night_gate.THERMAL_ARGV]
  873          if (row.get("hard_probe_errors") or not ac or any(p.get("exit_code") != 0 or
  874                  "AC Power" not in p.get("stdout", "") for p in ac)):
  875              excluded.add("ac_not_AC_Power_or_probe_error")
  876          if row.get("hard_probe_errors") or not thermal:
  877              excluded.add("CPU_Speed_Limit_below_100_or_thermal_probe_error")
  878          for probe in thermal:
  879              limits = [line.strip() for line in probe.get("stdout", "").splitlines()
  880                        if line.strip().startswith("CPU_Speed_Limit")]
  881              if probe.get("exit_code") != 0 or any(
  882                      re.fullmatch(r"CPU_Speed_Limit\s*=\s*\d+", line) is None or
  883                      int(line.split("=")[1]) < 100 for line in limits):
  884                  excluded.add("CPU_Speed_Limit_below_100_or_thermal_probe_error")
  885      return sorted(excluded)
```

### A3g `chi_square_lower_decile` — `joulewise/quiet_predicate_campaign.py:888-915`

```python
  888  def chi_square_lower_decile(df):
  889      """Invert regularized lower gamma P(df/2, x/2), using only stdlib.
  890  
  891      The pilot needs df=3..5; support 3..11 for diagnostic cross-checks.
  892      At the lower decile x/2 < df/2, so the positive gamma series converges
  893      quickly without subtracting a nearly-one upper-tail probability.
  894      """
  895      if type(df) is not int or not 3 <= df <= 11:
  896          raise ValueError("chi-square degrees of freedom must be in 3..11")
  897      shape = df / 2
  898      low, high = 0., float(df)
  899      for _ in range(80):
  900          mid = (low + high) / 2
  901          x = mid / 2
  902          term = total = 1 / shape
  903          for k in range(1, 1000):
  904              term *= x / (shape + k)
  905              total += term
  906              if term <= total * 1e-15:
  907                  break
  908          else:
  909              raise ArithmeticError("lower gamma series did not converge")
  910          probability = total * math.exp(-x + shape * math.log(x) - math.lgamma(shape))
  911          if probability < .10:
  912              low = mid
  913          else:
  914              high = mid
  915      return (low + high) / 2
```

## A4 — `joulewise/evidence_night.py`: the arm-notice text that states the busy-cores role

_A4 notice text: hit at line 273; enclosing function `render_notice`._

### A4 notice text (hit line 273, enclosing `render_notice`) — `joulewise/evidence_night.py:258-288`

```python
  258  
  259  def notice_subject(state):
  260      return f'NIGHT NOTICE — {state["plan_id"]} (EVIDENCE; DIAGNOSTIC_NO_PACK) — attempt {state["attempt"]}'
  261  
  262  
  263  def render_notice(state, *, checked=None, check_sha256=None):
  264      s = state["schedule"]
  265      lines = ["DRAFT — NOT SENT; prerequisites and veto observations are not yet recorded.",
  266               "To: claude2.glaring610@passmail.net",
  267               'Subject: ' + notice_subject(state),
  268               "", "Ed,", "Launch needs no action from you unless you reply NO. Your NO overrides.",
  269               f'Arm attempt {state["attempt"]}; prior candidates for this date: {", ".join(state["prior_candidates"]) or "none"}.',
  270               "This first idle-variance evidence night sizes a later experiment; it activates no new quietness cutoff.",
  271               "After 600 seconds settling, twelve 600-second idle envelopes use 480-second interiors after 60-second offsets.",
  272               "Power sampling is every 100 ms, with census, AC-power, thermal, timing and cleanup observations and a busy-cores journal.",
  273               "Busy cores remain a descriptive covariate. The 7,800-second program fits inside 9,000 seconds; no top-up or automatic repeat.",
  274               "Partial observations and refusals are kept. No model, load generator, calibration-ledger session or measurement pack runs.",
  275               "The scheduler supervises the program and the courier emails the result. Evidence remains PROVISIONAL.",
  276               "During the night exactly one read-only git show verifies chain bytes in the clone; no commit, push, checkout or fetch (87a F2).",
  277               "After delivery the lead sizes block two or records 'no cutoff qualifies'.",
  278               f'plan_id: {state["plan_id"]}', f'repo_head = measurement_head = H: {state["head"]}',
  279               f'clone: {state["measurement_root"]}', f'custody: {state["custody_root"]}',
  280               f'runs: {state["custody_root"]}/runs', f'staged plan: {state["plan_path"]}',
  281               f'authored_epoch_s: {json.loads(Path(state["plan_path"]).read_text())["authored_epoch_s"]}']
  282      for name, epoch in s["boundaries"].items():
  283          lines.append(f"{name}: {datetime.fromtimestamp(epoch).astimezone().isoformat()} "
  284                       f"{datetime.fromtimestamp(epoch, timezone.utc).isoformat()} epoch {epoch}")
  285      for name in ("registration", "chain_source"):
  286          lines.append(f'{state["bindings"][name + "_path"]} sha256 {state["bindings"][name + "_sha256"]}')
  287      for index, (start, end) in enumerate(s["install_spans_today"], 1):
  288          for boundary, epoch in (("open", start), ("close EXCLUDED", end)):
```

## A5 — `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v2.json` (complete) and its digest

```
sha256(git show 91f80870:configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v2.json) = 2c5392401a7956dfbb30f316a084541e0f53f214a4ce98c7d56d595ddb2779f1
night_gate.QPE01_PILOT_REGISTRATION_SHA256 = 2c5392401a7956dfbb30f316a084541e0f53f214a4ce98c7d56d595ddb2779f1
MATCH = True
```

### A5 registration (complete) — `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v2.json:1-82`

```json
    1  {
    2    "block_two": {
    3      "authored_after_pilot": true,
    4      "contrast": "idle-load-idle bracket",
    5      "levels": [
    6        0,
    7        0.05
    8      ],
    9      "one_profile": true,
   10      "one_qos": true,
   11      "smallest_holdable_share": 0.05,
   12      "upper_bound": "one-sided 95% paired-contrast upper bound"
   13    },
   14    "busy_cores_role": "covariate_only",
   15    "cadence_exclusion": "start_drift: absolute collector start drift greater than 10 s from the frozen schedule",
   16    "chain_source_sha256": "568a2771b28da9d805cd23ff4059bbbc27d6dfad1f8d9603331a412e3751b7ea",
   17    "envelope_s": 600,
   18    "envelopes": 12,
   19    "exclusions": [
   20      "census_not_clean_or_unknown",
   21      "ac_not_AC_Power_or_probe_error",
   22      "CPU_Speed_Limit_below_100_or_thermal_probe_error",
   23      "clock_anchor_unresolved",
   24      "incomplete_interior_support",
   25      "collect_error",
   26      "cleanup_unproven",
   27      "start_drift",
   28      "network_time_slew_attested",
   29      "network_time_unattested"
   30    ],
   31    "interior_offset_s": 60,
   32    "interior_s": 480,
   33    "load_generator": false,
   34    "minimum_adjacent_pairs": 4,
   35    "minimum_retained": 8,
   36    "pairing_rule": "disjoint_original_adjacent_pairs_both_retained_no_bridging",
   37    "power_interval_ms": 100,
   38    "receipt_class": "DIAGNOSTIC_NO_PACK",
   39    "recorder_journal": "evidence_busy_cores.jsonl",
   40    "ruling": "cold gate 10 Q1/Q2 (2026-09-19); adjudication 10a; sizing ruling 46b; A269 cold gate 10 (2026-09-22) Q1(c)/Q2(a)/Q3",
   41    "sample_interval_s": 30,
   42    "schema": "joulewise.quiet_predicate_pilot.v1",
   43    "settle_s": 600,
   44    "sizing": {
   45      "assumption": "independent normally distributed disjoint pair differences",
   46      "chi_square_lower_tail_probability": 0.1,
   47      "confidence": 0.9,
   48      "delta_j": 1,
   49      "formula": "max(3, ceil(8 * s_upper**2 / delta_j**2))",
   50      "maximum_pairs": 24,
   51      "minimum_pairs": 3,
   52      "multiplier": 8,
   53      "reference_factors": {
   54        "n_4": 2.266,
   55        "n_6": 1.762
   56      },
   57      "s_pair": "sample SD of retained disjoint differences, df = n - 1",
   58      "s_upper": "s_pair * sqrt((n - 1) / chi_square_quantile(0.10, n - 1))"
   59    },
   60    "slot_pitch_s": 620,
   61    "start_drift_abort_s": 2,
   62    "start_drift_max_s": 10,
   63    "stop_branches": {
   64      "block_two_upper_bound_above_1_J": "no cutoff qualifies",
   65      "observer_floor_above_smallest_holdable_share": "no cutoff qualifies",
   66      "sized_pairs_above_24": "no cutoff qualifies"
   67    },
   68    "summary": [
   69      "interior rail-sum and combined joules",
   70      "retained disjoint pairs (e1,e2), (e3,e4), ..., (e11,e12); even minus odd interior joules; sample SD and upper 90% bound",
   71      "overlapping adjacent differences and SD, maximum absolute difference: diagnostics only, never sizing",
   72      "all single-envelope values and SD, first-to-last retained drift: diagnostics only, never sizing",
   73      "name every overlapping original adjacent pair with absolute difference above 3 * s_pair; diagnostic only; never exclude by magnitude",
   74      "whole-round observer cpu-s, self plus reaped children including recorder; never subtracted",
   75      "recorder journal joined by monotonic support: per-envelope busy-core median/max and clean-machine distribution; covariates only",
   76      "cadence and native sample counts",
   77      "boot_id, os_build, sw_vers, powermetrics identity",
   78      "all named exclusions; partial observations retained; PROVISIONAL, no cutoff authority"
   79    ],
   80    "top_up": false,
   81    "window_max_s": 9000
   82  }
```

## A6 — agent census argv and the foreign-pid classifier

### A6a `AGENT_CENSUS_ARGV` — `joulewise/night_gate.py:137-137`

```python
  137  AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-lf", "[c]odex|[c]laude|[t]3")
```

### A6b `agent_census` — `joulewise/night_gate.py:621-648`

```python
  621  def agent_census(probes: CensusProbes) -> tuple[ProbeResult, Refusal | None]:
  622      try:
  623          result = _run(probes, AGENT_CENSUS_ARGV)
  624      except ProbeError as exc:
  625          try:
  626              observed_monotonic_ns = _safe_monotonic_ns(probes)
  627          except ProbeError as clock_exc:
  628              observed_monotonic_ns = 0
  629              exc = ProbeError(f"{exc}; {clock_exc}")
  630          result = ProbeResult(
  631              argv=AGENT_CENSUS_ARGV,
  632              exit_code=-1,
  633              stdout="",
  634              stderr=str(exc),
  635              monotonic_ns=observed_monotonic_ns,
  636          )
  637          return result, Refusal("night_probe_error", str(exc), (result,))
  638      if result.exit_code == 1 and result.stdout.strip() == "":
  639          return result, None
  640      lines = result.stdout.strip().splitlines()
  641      detail = f"pgrep exit {result.exit_code}"
  642      if lines:
  643          shown = lines[:20]
  644          bounded = "\n".join(shown)
  645          if len(lines) > len(shown):
  646              bounded += f"\n… (+{len(lines) - len(shown)} more)"
  647          detail += f"; forbidden process output: {bounded}"
  648      return result, Refusal("night_refused_agent_present", detail, (result,))
```

### A6c `classify_arm_census` — `joulewise/arm_census.py:206-239`

```python
  206  def classify_arm_census(plan: NightPlan, observation: Observation, *, caller_pid: int) -> Verdict:
  207      """Classify one observation without process reads, effects or night policy."""
  208      own = _ancestors(observation.inventory, caller_pid)
  209      records = {row.pid: row for row in observation.records}
  210      relevant = set().union(*(
  211          _ancestors(observation.inventory, pid) for pid in observation.hit_pids
  212      )) if observation.hit_pids else set()
  213      roots = {pid for pid in relevant if pid in records and _interactive_root(records[pid])}
  214      # Exact ancestry finds roots even when discovery omits them; an unreadable
  215      # own-chain discovery hit still anchors descendant workload scanning.
  216      own_root = _own_root(observation.inventory, records, caller_pid, set(observation.hit_pids))
  217      if own_root is not None:
  218          roots.add(own_root)
  219      workloads: dict[int, str] = {}
  220      sessions = []
  221      exempt = set(own)
  222      for pid in sorted(roots):
  223          descendants = observation.inventory.descendants(pid)
  224          work = tuple(
  225              (child, category)
  226              for child in sorted(descendants - own)
  227              if child in records and (category := _workload(records[child])) is not None
  228          )
  229          workloads.update(work)
  230          idle_exemption = plan.receipt_class == "REHEARSAL_STUB" and not work and (
  231              pid in own or (pid in records and _interactive_root(records[pid]))
  232          )
  233          if idle_exemption:
  234              exempt.update(descendants | {pid})
  235          sessions.append(Session(pid, tuple(sorted(descendants)), work, idle_exemption))
  236      # Missing/unreadable exact records are unknown, hence idle, with diagnostics.
  237      foreign = (set(observation.hit_pids) & records.keys()) - exempt
  238      return Verdict(plan.receipt_class, tuple(sorted(own)), tuple(sessions),
  239                     tuple(sorted(foreign)), tuple(sorted(workloads.items())), observation.diagnostics)
```

