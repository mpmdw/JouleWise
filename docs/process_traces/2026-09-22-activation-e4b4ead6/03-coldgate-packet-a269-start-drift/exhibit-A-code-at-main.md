# Exhibit A — code at main `ecbc0fac` (verbatim `git show ecbc0fac:<path>` extracts located by `ast`, printed with 1-based line numbers)

## A — `joulewise/quiet_predicate_campaign.py:41-47` `frozen_protocol`

```python
   41  def frozen_protocol(raw=None):
   42      """The byte-pinned registration is the single source of protocol values."""
   43      if raw is None:
   44          raw = (Path(__file__).resolve().parents[1] / PROTOCOL_PATH).read_bytes()
   45      if digest(raw) != night_gate.QPE01_PILOT_REGISTRATION_SHA256:
   46          raise ValueError("protocol is not the ruled pilot registration")
   47      return json.loads(raw)
```

## A — `joulewise/quiet_predicate_campaign.py:50-53` `validate_protocol`

```python
   50  def validate_protocol(protocol, source_digest):
   51      if protocol != frozen_protocol() or protocol.get("chain_source_sha256") != source_digest:
   52          raise ValueError("frozen pilot protocol mismatch; CLI overrides are forbidden")
   53      return protocol
```

## A — `joulewise/quiet_predicate_campaign.py:132-147` `process_groups`

```python
  132  def process_groups(path):
  133      if not path.exists():
  134          return set()  # A pre-execute refusal launched no supervised children.
  135      groups = set()
  136      for line in path.read_text().splitlines():
  137          row = json.loads(line)
  138          if not isinstance(row, dict):
  139              raise ValueError("invalid evidence process journal row")
  140          pgid = row["pgid"]
  141          if type(pgid) is not int or pgid <= 1 or pgid == os.getpgrp():
  142              raise ValueError("unsafe evidence process group identity")
  143          if row.get("state") == "absent":
  144              groups.discard(pgid)
  145          else:
  146              groups.add(pgid)
  147      return groups
```

## A — `joulewise/quiet_predicate_campaign.py:150-196` `cleanup_groups`

```python
  150  def cleanup_groups(path, children=(), budget_s=30, exclude=()):
  151      """One budget for TERM, KILL, reaping and all group censuses; fail closed."""
  152      deadline = time.monotonic() + budget_s
  153      term_until = min(deadline, time.monotonic() + min(20, budget_s * .67))
  154      known, checked, errors, signal_errors = set(), set(), [], []
  155      pending = set()
  156      while time.monotonic() < deadline:
  157          for child in children:
  158              child.poll()
  159          try:
  160              pending = process_groups(path) - set(exclude)
  161          except (OSError, ValueError, KeyError) as exc:
  162              errors.append(str(exc))
  163              break
  164          known.update(pending)
  165          for pgid in sorted(pending):
  166              if time.monotonic() >= deadline:
  167                  break
  168              try:
  169                  if group_absent(pgid):
  170                      append_event(path, {"kind": "cleanup", "pgid": pgid, "state": "absent"})
  171                      checked.add(pgid)
  172                  else:
  173                      os.killpg(pgid, signal.SIGTERM if time.monotonic() < term_until else signal.SIGKILL)
  174              except ProcessLookupError:
  175                  pass  # Only the next census can prove absence.
  176              except PermissionError as exc:
  177                  signal_errors.append(f"pgid={pgid}: {exc}")
  178              except OSError as exc:
  179                  errors.append(str(exc))
  180          if pending <= checked:
  181              # New groups journaled during teardown must be included too.
  182              try:
  183                  if not (process_groups(path) - set(exclude)):
  184                      break
  185              except (OSError, ValueError, KeyError) as exc:
  186                  errors.append(str(exc))
  187                  break
  188          time.sleep(min(.05, max(0, deadline - time.monotonic())))
  189      try:
  190          pending = process_groups(path) - set(exclude)
  191      except (OSError, ValueError, KeyError) as exc:
  192          errors.append(str(exc))
  193      residue = sorted((known - checked) | pending)
  194      return {"budget_s": budget_s, "groups": sorted(known), "residue": residue,
  195              "signal_errors": sorted(set(signal_errors)),
  196              "errors": sorted(set(errors)), "cleanup_proven": not residue and not errors}
```

## A — `joulewise/quiet_predicate_campaign.py:240-262` `hard_exclusions`

```python
  240  def hard_exclusions(rows):
  241      """Named mechanisms only. This function never reads busy-core values."""
  242      excluded = set()
  243      if not rows or any(row.get("census_clean") is not True for row in rows):
  244          excluded.add("census_not_clean_or_unknown")
  245      for row in rows:
  246          batches = row.get("hard_probes") or []
  247          probes = [probe for batch in batches for probe in batch.get("result", [])]
  248          ac = [p for p in probes if tuple(p.get("argv", [])) == night_gate.PMSET_BATT_ARGV]
  249          thermal = [p for p in probes if tuple(p.get("argv", [])) == night_gate.THERMAL_ARGV]
  250          if (row.get("hard_probe_errors") or not ac or any(p.get("exit_code") != 0 or
  251                  "AC Power" not in p.get("stdout", "") for p in ac)):
  252              excluded.add("ac_not_AC_Power_or_probe_error")
  253          if row.get("hard_probe_errors") or not thermal:
  254              excluded.add("CPU_Speed_Limit_below_100_or_thermal_probe_error")
  255          for probe in thermal:
  256              limits = [line.strip() for line in probe.get("stdout", "").splitlines()
  257                        if line.strip().startswith("CPU_Speed_Limit")]
  258              if probe.get("exit_code") != 0 or any(
  259                      re.fullmatch(r"CPU_Speed_Limit\s*=\s*\d+", line) is None or
  260                      int(line.split("=")[1]) < 100 for line in limits):
  261                  excluded.add("CPU_Speed_Limit_below_100_or_thermal_probe_error")
  262      return sorted(excluded)
```

## A — `joulewise/quiet_predicate_campaign.py:320-446` `pilot_summary`

```python
  320  def pilot_summary(directory, protocol, envelopes, observer_cpu_s=None):
  321      """Apply ruling 46b to fixed pairs; preserve unfiltered diagnostics."""
  322      import statistics
  323      from scripts import sample_quiet_predicate_evidence as harness
  324      values, all_rows = [], []
  325      journal = directory.parent / protocol["recorder_journal"]
  326      covariates = [json.loads(line) for line in journal.read_text().splitlines() if line] if journal.exists() else []
  327      clean_busy = []
  328      for entry in envelopes:
  329          excluded = []
  330          if entry.get("collector_exit", 0) != 0:
  331              excluded.append("collect_error")
  332          if entry.get("cleanup", {}).get("cleanup_proven") is False:
  333              excluded.append("cleanup_unproven")
  334          scheduled = entry.get("scheduled_mono_s")
  335          support = [r for r in covariates if scheduled is not None and
  336                     r["monotonic_start"] >= scheduled and
  337                     r["monotonic_end"] <= scheduled + protocol["envelope_s"]]
  338          busy = [(r.get("observation") or {}).get("metrics", {}).get("busy_cores") for r in support]
  339          distribution = harness.quantiles(busy)
  340          entry = {**entry, "busy_cores": {**distribution, "median": distribution["p50"]},
  341                   "busy_cores_samples": len([v for v in busy if harness.number(v) is not None]),
  342                   "recorder_observer_cpu_s": sum(r.get("observer_cpu_s") or 0 for r in support)}
  343          out = directory / f"envelope-{entry['index']:02d}"
  344          try:
  345              session = json.loads((out / "session.json").read_text())
  346              rows = [json.loads(line) for line in (out / "rounds.jsonl").read_text().splitlines() if line]
  347          except (OSError, ValueError) as exc:
  348              values.append({**entry, "excluded": excluded + ["incomplete_interior_support"], "error": str(exc), "joules": None})
  349              continue
  350          all_rows.extend(rows)
  351          hard = hard_exclusions(rows)
  352          excluded.extend(hard)
  353          if not hard:
  354              clean_busy.extend(busy)
  355          interior = session.get("interior", {})
  356          if (session.get("power") or {}).get("anchor", {}).get("status") != "bounded":
  357              excluded.append("clock_anchor_unresolved")
  358          if not interior.get("complete_support"):
  359              excluded.append("incomplete_interior_support")
  360          entry = {**entry, "collector_start_drift_s": session.get("start_drift_s")}
  361          if max(abs(entry["start_drift_s"]), abs(session.get("start_drift_s") or 0)) > protocol["start_drift_max_s"]:
  362              excluded.append("start_drift")
  363          if any(row.get("os_build_valid") is not True or row.get("os_build") != session.get("os_build") or
  364                 row.get("session") != session.get("session") for row in rows):
  365              raise ValueError("pilot row/session identity mismatch")
  366          energy = (interior.get("power") or {}).get("energy_j", {})
  367          values.append({**entry, "excluded": sorted(set(excluded)), "interior": interior,
  368                         "joules": energy.get("rail_sum_w"), "combined_joules": energy.get("combined_w"),
  369                         "boot_id": session.get("boot_id"), "os_build": session.get("os_build"),
  370                         "sw_vers": session.get("sw_vers"), "powermetrics_identity": session.get("powermetrics_identity"),
  371                         "whole_envelope_observer_cpu_s": session.get("whole_envelope_observer_cpu_s"),
  372                         "observer_cpu_s": sum(row.get("observer_cpu_s") or 0 for row in rows),
  373                         "censuses": [{"round": r["round"], "clean": r.get("census_clean")} for r in rows]})
  374      retained = [v for v in values if not v["excluded"] and v["joules"] is not None]
  375      # Index identity, not position in a filtered list, fixes the original pairs.
  376      by_index = {v["index"]: v for v in values}
  377      overlapping = []
  378      for index in range(1, protocol["envelopes"]):
  379          a, b = by_index.get(index), by_index.get(index + 1)
  380          if a is None or b is None or a["joules"] is None or b["joules"] is None:
  381              continue
  382          overlapping.append({"left": index, "right": index + 1,
  383              "delta_j": b["joules"] - a["joules"],
  384              "retained": not a["excluded"] and not b["excluded"]
  385                  and a.get("boot_id") == b.get("boot_id") and a.get("os_build") == b.get("os_build")})
  386      deltas = [d for d in overlapping if d["retained"] and d["left"] % 2 == 1]
  387      sufficient = len(retained) >= protocol["minimum_retained"] and len(deltas) >= protocol["minimum_adjacent_pairs"]
  388      pair_sd = statistics.stdev(d["delta_j"] for d in deltas) if len(deltas) >= 2 else None
  389      df = len(deltas) - 1 if len(deltas) >= 2 else None
  390      factor = math.sqrt(df / chi_square_lower_decile(df)) if sufficient else None
  391      s_upper = pair_sd * factor if sufficient else None
  392      # Whole-round measured cost, including rejected envelopes; never subtract
  393      # it from energy or use it as an envelope retention input.
  394      observer_rows = [r for r in all_rows if harness.number(r.get("observer_cpu_s")) is not None
  395                       and harness.number(r.get("round_mono_start_s")) is not None
  396                       and harness.number(r.get("round_mono_end_s")) is not None
  397                       and r["round_mono_end_s"] > r["round_mono_start_s"]]
  398      observer_support_s = sum(r["round_mono_end_s"] - r["round_mono_start_s"] for r in observer_rows)
  399      observer_floor = sum(r["observer_cpu_s"] for r in observer_rows) / observer_support_s if observer_support_s else None
  400      stop = stop_branch(s_upper=s_upper, observer_floor=observer_floor, protocol=protocol)
  401      unfiltered = [v["joules"] for v in values if v["joules"] is not None]
  402      large_pairs = [d for d in overlapping if pair_sd is not None and abs(d["delta_j"]) > 3 * pair_sd]
  403      report = {"schema": "joulewise.quiet_predicate_pilot_summary.v1", "evidence_status": "PROVISIONAL",
  404          "status": "SPREAD_RECORDED" if sufficient else "INCONCLUSIVE", "envelopes": values,
  405          "retained": len(retained), "sizing_pairs": deltas, "retained_pairs": len(deltas),
  406          "adjacent_pairs": overlapping, "adjacent_pairs_role": "diagnostic_only; never used for sizing",
  407          "adjacent_pair_sd_j": statistics.stdev(d["delta_j"] for d in overlapping) if len(overlapping) >= 2 else None,
  408          "pair_sd_j": pair_sd, "pair_df": df, "s_upper_factor": factor,
  409          "single_envelope_sd_j": statistics.stdev(v["joules"] for v in retained) if len(retained) >= 2 else None,
  410          "unfiltered_single_envelope_sd_j": statistics.stdev(unfiltered) if len(unfiltered) >= 2 else None,
  411          "single_envelope_role": "diagnostic_only; never used for sizing",
  412          "first_to_last_retained_drift_j": retained[-1]["joules"] - retained[0]["joules"] if len(retained) >= 2 else None,
  413          "pairs_above_3_pair_sd": large_pairs,
  414          "pairs_above_3_pair_sd_role": "overlapping adjacent differences; diagnostic only",
  415          "max_abs_delta_j": max((abs(d["delta_j"]) for d in overlapping), default=None),
  416          "busy_cores": harness.quantiles(clean_busy), "busy_cores_role": "covariate_only; never excluded",
  417          "busy_cores_source": protocol["recorder_journal"],
  418          "busy_cores_support": "recorder intervals fully within each scheduled envelope",
  419          "clean_machine_busy_cores": harness.quantiles(clean_busy),
  420          "clean_machine_definition": "envelopes passing census, AC and thermal hard probes; independent of energy retention",
  421          "observer_floor_cores": observer_floor, "observer_support_s": observer_support_s,
  422          "s_upper": s_upper,
  423          "s_upper_reason": "one-sided upper 90% chi-square bound; independent normal pair differences assumed"
  424              if sufficient else "fewer than four retained disjoint pairs or eight retained envelopes; no top-up",
  425          "block_two_pairs": stop["pairs"], "block_two_stop": stop,
  426          "block_two_pairs_reason": "ruling 46b: " + protocol["sizing"]["formula"] +
  427              f"; delta_j={protocol['sizing']['delta_j']}; stop above {protocol['sizing']['maximum_pairs']} pairs"
  428              if sufficient else "INCONCLUSIVE; no sizing",
  429          "whole_campaign_observer_cpu_s": observer_cpu_s,
  430          "observer_definition": "SELF + reaped CHILDREN, including collector, recorder, sampler and census; never subtracted",
  431          "cutoff_authority": False, "top_up": False}
  432      harness.write_json(directory / "summary.json", report)
  433      (directory / "summary.md").write_text(
  434          "# QPE-01 pilot (PROVISIONAL, descriptive)\n\n" +
  435          f"Status: {report['status']}. Retained {len(retained)}/{protocol['envelopes']} envelopes; {len(deltas)} disjoint pairs.\n\n" +
  436          f"Disjoint-pair sample SD: {pair_sd} J (df={df}); upper 90% bound: {s_upper} J. " +
  437          "This chi-square construction assumes independent, normally distributed pair differences.\n\n" +
  438          f"Block-two pairs: {stop['pairs']}; sizing stop: {stop['outcome']}. No sizing when INCONCLUSIVE.\n\n" +
  439          f"Diagnostics only: {len(overlapping)} overlapping differences (SD {report['adjacent_pair_sd_j']} J); " +
  440          f"single-envelope SD {report['unfiltered_single_envelope_sd_j']} J; " +
  441          f"first-to-last retained drift {report['first_to_last_retained_drift_j']} J. " +
  442          f"Overlapping adjacent pairs with |delta| > 3 * s_pair: {large_pairs}. Values are in summary.json.\n\n" +
  443          "Busy cores are recorded covariates and never an exclusion input. " +
  444          "Every exclusion and partial interior is retained in summary.json. No top-up, cutoff or activation authority. " +
  445          "Block two is not authored by this summary.\n")
  446      return report
```

## A — `joulewise/quiet_predicate_campaign.py:449-526` `execute`

```python
  449  def execute(plan, protocol, night_dir):
  450      """No schedule knobs: all quantities come from the authenticated protocol."""
  451      from scripts import sample_quiet_predicate_evidence as harness
  452      night_dir.mkdir(parents=True, exist_ok=True)
  453      directory = night_dir / "evidence"
  454      directory.mkdir()  # no overwrite/retry
  455      journal = night_dir / "evidence_processes.jsonl"
  456      journal.touch(exist_ok=False)
  457      env = {**os.environ, "EVIDENCE_PROCESS_JOURNAL": str(journal)}
  458      children, envelopes = [], []
  459      consecutive_cleanup_failures = 0
  460      outcome, error = "refused", None
  461      cpu_start = harness.cpu_total()
  462      go = time.monotonic()
  463      def interrupted(signum, _frame):
  464          raise InterruptedError(f"evidence chain signal {signum}")
  465      old = {s: signal.signal(s, interrupted) for s in (signal.SIGTERM, signal.SIGINT)}
  466      def launch(kind, argv):
  467          process = subprocess.Popen(argv, env=env, stdin=subprocess.DEVNULL, start_new_session=True)
  468          children.append(process)
  469          append_event(journal, {"kind": kind, "pgid": process.pid, "epoch_s": time.time()})
  470          return process
  471      try:
  472          # Settle belongs inside GO; verify-only never reaches this call.
  473          print(f"evidence_settle seconds={protocol['settle_s']}", flush=True)
  474          time.sleep(protocol["settle_s"])
  475          first = go + protocol["settle_s"]
  476          recorder = launch("recorder", [sys.executable, "-B", "-m", "joulewise.quiet_predicate_campaign", "record"])
  477          for index in range(1, protocol["envelopes"] + 1):
  478              scheduled = first + (index - 1) * protocol["envelope_s"]
  479              time.sleep(max(0, scheduled - time.monotonic()))
  480              if time.time() + protocol["envelope_s"] > plan.t0_epoch_s + plan.window_max_s:
  481                  raise ValueError("evidence window exhausted; no compressed envelope or top-up")
  482              actual = time.monotonic()
  483              out = directory / f"envelope-{index:02d}"
  484              collector = launch("collector", [sys.executable, "-B", str(Path(plan.measurement_root) / HARNESS_PATHS[0]),
  485                  "collect", "--state", "idle", "--repeat", str(index), "--duration-s", str(protocol["envelope_s"]),
  486                  "--sample-interval-s", str(protocol["sample_interval_s"]), "--interior-offset-s", str(protocol["interior_offset_s"]),
  487                  "--interior-s", str(protocol["interior_s"]), "--envelope-start-mono-s", str(scheduled), "--power-interval-ms", str(protocol["power_interval_ms"]), "--out", str(out)])
  488              print(f"envelope_start index={index} collector_pgid={collector.pid} recorder_pgid={recorder.pid}", flush=True)
  489              try:
  490                  code = collector.wait(timeout=protocol["envelope_s"] + 30)
  491              except subprocess.TimeoutExpired:
  492                  code = 124
  493              # The covariate recorder spans all envelopes. Each collector and
  494              # its independent sampler/power groups must be reaped between slots.
  495              cleanup = cleanup_groups(journal, children, budget_s=30, exclude={recorder.pid})
  496              envelopes.append({"index": index, "scheduled_mono_s": scheduled, "actual_mono_s": actual,
  497                                "start_drift_s": actual - scheduled, "collector_exit": code, "cleanup": cleanup})
  498              append_event(night_dir / "evidence_envelopes.jsonl", envelopes[-1])
  499              print(f"envelope_end index={index} rc={code} cleanup_proven={cleanup['cleanup_proven']}", flush=True)
  500              consecutive_cleanup_failures = 0 if cleanup["cleanup_proven"] else consecutive_cleanup_failures + 1
  501              if consecutive_cleanup_failures >= 2:
  502                  raise ValueError("two consecutive cleanup_unproven envelopes")
  503              if recorder.poll() is not None:
  504                  raise ValueError("evidence covariate recorder exited early")
  505          outcome = "partial" if any(e["collector_exit"] != 0 or not e["cleanup"]["cleanup_proven"] for e in envelopes) else "complete"
  506      except (OSError, ValueError, KeyboardInterrupt, subprocess.SubprocessError) as exc:
  507          error = f"{type(exc).__name__}: {exc}"
  508      finally:
  509          for signum in old:
  510              signal.signal(signum, signal.SIG_IGN)
  511          cleanup = cleanup_record(night_dir, children)
  512          try:
  513              pilot_summary(directory, protocol, envelopes,
  514                            harness.cpu_total() - cpu_start if cleanup["cleanup_proven"] else None)
  515          except (OSError, ValueError, KeyError, TypeError) as exc:
  516              outcome, error = "refused", "pilot summary failed: " + str(exc)
  517          if not cleanup["cleanup_proven"]:
  518              outcome, error = "refused", error or "final evidence cleanup unproven"
  519          if outcome == "refused":
  520              write_refusal(night_dir, plan, error or "evidence execution aborted")
  521          harness.write_json(night_dir / "evidence_outcome.json", {"outcome": outcome, "error": error,
  522              "envelopes_attempted": len(envelopes), "cleanup_proven": cleanup["cleanup_proven"]})
  523          for signum, handler in old.items():
  524              signal.signal(signum, handler)
  525      print(f"evidence_end outcome={outcome} cleanup_proven={cleanup['cleanup_proven']}", flush=True)
  526      return 0 if outcome in {"complete", "partial"} and cleanup["cleanup_proven"] else 2
```

## A — `scripts/run_night.py:3413-3435` `_group_census`

```python
 3413  def _group_census(pgid: int, timeout_s: float = 1) -> tuple[bool, list[str]]:
 3414      """Census one process group: (absent, the lines the census listed).
 3415  
 3416      ABSENT means one thing only: `pgrep` exited 1 (its "no process matched"
 3417      status) with empty output. Exit 0 lists live members. Exit 2 means the
 3418      argument was malformed and nothing was searched; an OSError or a timeout
 3419      means the census did not run. None of those three establishes absence, so
 3420      each of them returns False and carries its own evidence line: a census
 3421      that could not answer is never read as an empty group.
 3422      """
 3423  
 3424      # pgrep also works where the sandbox denies killpg(..., 0) after exit.
 3425      try:
 3426          result = subprocess.run(["/usr/bin/pgrep", "-lf", "-g", str(pgid), "."],
 3427                                  capture_output=True, text=True, timeout=timeout_s, check=False)
 3428      except (OSError, subprocess.SubprocessError) as error:
 3429          return False, [f"census_failed: {type(error).__name__}: {error}"]
 3430      lines = [line for line in result.stdout.splitlines() if line.strip()]
 3431      if result.returncode == 1 and not lines:
 3432          return True, []
 3433      if result.returncode not in {0, 1}:
 3434          lines = [f"census_exit_{result.returncode}: {result.stderr.strip()}", *lines]
 3435      return False, lines
```

## A — `scripts/sample_quiet_predicate_evidence.py:560-667` `PowerRecorder`

```python
  560  class PowerRecorder:
  561      def __init__(self, path, interval_ms, clock, deadline):
  562          self.path, self.clock, self.deadline = path, clock, deadline
  563          self.argv = power_argv(path, interval_ms)
  564          self.process = None
  565          self.stamps = {}
  566          self.timer = None
  567          self.kill_timer = None
  568          self.stop_lock = threading.Lock()
  569          self.metadata = {"argv": self.argv, "identity": None, "processes": None, "cleanup": None,
  570                           "term_sent": False, "kill_sent": False}
  571  
  572      def start(self):
  573          self.stamps["pre_spawn"] = self.clock.stamp()
  574          stderr = self.path.with_suffix(".stderr")
  575          with stderr.open("wb") as stream:
  576              self.process = subprocess.Popen(self.argv, stdin=subprocess.DEVNULL,
  577                                              stdout=subprocess.DEVNULL, stderr=stream,
  578                                              start_new_session=True)
  579          from joulewise.quiet_predicate_campaign import journal_process
  580          journal_process("power", self.process.pid)
  581          self.timer = threading.Timer(max(0, self.deadline - self.clock.monotonic()), self.request_stop)
  582          self.timer.daemon = True
  583          self.timer.start()
  584          # Observe first complete frame promptly; this stamp is a causal bound,
  585          # never a sample timestamp. Delay ps identity lookup until after it.
  586          ready_until = min(self.deadline, self.clock.monotonic() + 15)
  587          while self.clock.monotonic() < ready_until:
  588              data = self.path.read_bytes() if self.path.exists() else b""
  589              if b"</plist>" in data:
  590                  parse_frames(data)  # The stamp follows a real complete-frame parse.
  591                  self.stamps["first_parse"] = self.clock.stamp()
  592                  self.stamps["sampling_started"] = self.clock.stamp()
  593                  self.metadata["identity"] = identity(self.process.pid)
  594                  tree = command_text(quiet_admission.PS_ARGV)
  595                  if isinstance(tree, str):
  596                      self.path.with_suffix(".processes.txt").write_text(tree + "\n")
  597                      entries = list(quiet_admission.parse_ps(tree).values())
  598                      owned = {self.process.pid}
  599                      while (extended := owned | {p["pid"] for p in entries if p["ppid"] in owned}) != owned:
  600                          owned = extended
  601                      self.metadata["processes"] = [p for p in entries if p["pid"] in owned]
  602                  return
  603              if self.process.poll() is not None:
  604                  raise RuntimeError(f"powermetrics exited during startup: {self.process.returncode}")
  605              self.clock.sleep(.02)
  606          raise RuntimeError("powermetrics first complete frame unavailable by startup deadline")
  607  
  608      def request_stop(self):
  609          with self.stop_lock:
  610              if "sampling_stopped" not in self.stamps:
  611                  self.stamps["sampling_stopped"] = self.clock.stamp()
  612                  if self.process:
  613                      # Do not poll/wait here: reaping the recorder while the
  614                      # final observer bracket is open would charge the entire
  615                      # recorder's CPU to that one round's RUSAGE_CHILDREN.
  616                      # Signal the supervised sudo process, which forwards TERM
  617                      # using its launch privilege; do not signal the root group.
  618                      try:
  619                          os.kill(self.process.pid, signal.SIGTERM)
  620                          self.metadata["term_sent"] = True
  621                      except ProcessLookupError:
  622                          pass
  623                      except PermissionError as exc:
  624                          self.metadata.setdefault("signal_errors", []).append(str(exc))
  625                      self.kill_timer = threading.Timer(5, self.force_stop)
  626                      self.kill_timer.daemon = True
  627                      self.kill_timer.start()
  628  
  629      def force_stop(self):
  630          with self.stop_lock:
  631              if self.process:
  632                  try:
  633                      # Unreaped child PID cannot be reused. Signalling an
  634                      # already-exited zombie is harmless and is not reaping.
  635                      os.kill(self.process.pid, signal.SIGKILL)
  636                      self.metadata["kill_sent"] = True
  637                  except ProcessLookupError:
  638                      pass
  639                  except PermissionError as exc:
  640                      self.metadata.setdefault("signal_errors", []).append(str(exc))
  641  
  642      def finish(self):
  643          self.request_stop()
  644          if self.timer:
  645              self.timer.cancel()
  646          if self.process:
  647              remaining = max(0.0, 5 - (self.clock.monotonic() - self.stamps["sampling_stopped"].monotonic_before_s))
  648              try:
  649                  code = self.process.wait(timeout=remaining)
  650              except subprocess.TimeoutExpired:
  651                  self.force_stop()
  652                  try:
  653                      code = self.process.wait(timeout=5)
  654                  except subprocess.TimeoutExpired:
  655                      code = None
  656              self.metadata["cleanup"] = reasons({"returncode": code, "term": self.metadata["term_sent"],
  657                  "kill": code in (-signal.SIGKILL, 128 + signal.SIGKILL),
  658                  "reap_after_observer_bracket": True}, "process not reaped after KILL")
  659          if self.kill_timer:
  660              self.kill_timer.cancel()
  661          data = self.path.read_bytes() if self.path.exists() else b""
  662          frames, dropped = parse_frames(data) if data else ([], None)
  663          self.stamps["post_parse"] = self.clock.stamp()
  664          aligned, anchor = align_frames(frames, self.stamps)
  665          self.metadata.update(stamps={k: asdict(v) for k, v in self.stamps.items()},
  666                               anchor=anchor, dropped_final_frame=dropped)
  667          return aligned, anchor
```

## A — `scripts/sample_quiet_predicate_evidence.py:217-234` `align_frames`

```python
  217  def align_frames(frames, stamps, deriver=derive_powermetrics_anchor_v3):
  218      records = [NativeAnchorRecord(
  219          elapsed_s=f["elapsed_s"], native_timestamp_s=f["native_timestamp_s"],
  220          power_w=f["power"]["rail_sum_w"] if f["power"]["rail_sum_w"] is not None else math.nan,
  221          energy_j=f["energy_j"], is_delta=f["is_delta"],
  222          elapsed_ns=f["elapsed_ns"], native_timestamp_ns=f["native_timestamp_ns"])
  223          for f in frames]
  224      anchor = deriver(stamps=stamps, records=records)
  225      if anchor["status"] != "bounded":
  226          return [], anchor
  227      endpoint = anchor["first_sample_end_point_epoch_s"]
  228      aligned, elapsed_ns = [], 0
  229      for i, frame in enumerate(frames):
  230          if i:
  231              elapsed_ns += frame["elapsed_ns"]
  232          end = endpoint + elapsed_ns / 1e9
  233          aligned.append({**frame, "start_s": end - frame["elapsed_s"], "end_s": end})
  234      return aligned, anchor
```

## A — `scripts/sample_quiet_predicate_evidence.py:241-293` `integrate`

```python
  241  def integrate(frames, start, end, uncertainty_s=0.0):
  242      """Overlap seconds times watts; means divide by each rail's own coverage.
  243  
  244      For each averaging interval, moving either boundary by at most epsilon
  245      changes overlap by <=2*epsilon. Sum P_i*min(dt_i,2*epsilon) over frames
  246      touching the expanded round. This conservative interval-power bound does
  247      not shrink with sample count. Unobserved gaps have no finite energy bound.
  248      """
  249      if end <= start or uncertainty_s < 0:
  250          raise ValueError("invalid round support or alignment uncertainty")
  251      for left, right in zip(frames, frames[1:]):
  252          if right["start_s"] < left["end_s"] - 1e-6:
  253              raise ValueError("overlapping or unordered native supports")
  254      weighted = [(f, overlap(start, end, f["start_s"], f["end_s"])) for f in frames]
  255      coverage = math.fsum(w for _, w in weighted)
  256      energy, rail_coverage, bounds, power = {}, {}, {}, {}
  257      for rail in RAILS:
  258          selected = [(f["power"][rail], w) for f, w in weighted
  259                      if w > 0 and f["power"][rail] is not None]
  260          den = math.fsum(w for _, w in selected)
  261          expanded_coverage = math.fsum(overlap(start - uncertainty_s, end + uncertainty_s,
  262              f["start_s"], f["end_s"]) for f in frames if f["power"][rail] is not None)
  263          joules = math.fsum(p * w for p, w in selected)
  264          rail_coverage[rail] = den
  265          energy[rail] = joules if den else None
  266          power[rail] = joules / den if den else None
  267          bounds[rail] = (math.fsum(
  268              f["power"][rail] * min(f["elapsed_s"], 2 * uncertainty_s)
  269              for f in frames if f["power"][rail] is not None
  270              and overlap(start - uncertainty_s, end + uncertainty_s, f["start_s"], f["end_s"]) > 0)
  271              if expanded_coverage >= end - start + 2 * uncertainty_s - 1e-6 else None)
  272      power.update(coverage_s=coverage, rail_coverage_s=rail_coverage, energy_j=energy)
  273      def average_entities(kind, id_key, keys):
  274          ids = sorted({entry[id_key] for f, w in weighted if w > 0
  275                        for entry in f[kind] if entry[id_key] is not None}, key=str)
  276          result = []
  277          for entity in ids:
  278              row = {id_key: entity, "coverage_s": {}}
  279              for key in keys:
  280                  values = [(entry[key], w) for f, w in weighted if w > 0 for entry in f[kind]
  281                            if entry[id_key] == entity and entry[key] is not None]
  282                  den = math.fsum(w for _, w in values)
  283                  row[key] = math.fsum(v * w for v, w in values) / den if den else None
  284                  row["coverage_s"][key] = den
  285              result.append(reasons(row))
  286          return result
  287      return {
  288          "power": reasons(power, "no covered native samples for this rail"),
  289          "clusters": average_entities("clusters", "name", ("active_ratio", "idle_ratio", "down_ratio", "online_ratio", "freq_hz")) or None,
  290          "cpus": average_entities("cpus", "cpu", ("active_ratio", "freq_hz")) or None,
  291          "span_mismatch": abs(coverage - (end - start)) > 1e-6,
  292          "error_bound_j": bounds["rail_sum_w"], "rail_error_bound_j": reasons(bounds, "incomplete rail coverage; unobserved energy is unbounded"),
  293      }
```

## A — `scripts/sample_quiet_predicate_evidence.py:296-310` `reduce_interior`

```python
  296  def reduce_interior(frames, anchor, start, duration):
  297      """Integrate native interval supports; never rescale a whole-round mean."""
  298      result = {"start_epoch_s": start, "end_epoch_s": start + duration,
  299                "duration_s": duration, "complete_support": False, "status": "partial",
  300                "native_samples": 0, "power": None, "reason": "clock anchor unresolved"}
  301      if anchor.get("status") != "bounded":
  302          return reasons(result)
  303      values = integrate(frames, start, start + duration, anchor["effective_clock_anchor_bound_s"])
  304      complete = (not values["span_mismatch"] and all(
  305          abs(values["power"]["rail_coverage_s"][rail] - duration) <= 1e-6
  306          for rail in ("rail_sum_w", "combined_w")))
  307      result.update(values, complete_support=complete, status="complete" if complete else "partial",
  308                    native_samples=sum(overlap(start, start + duration, f["start_s"], f["end_s"]) > 0 for f in frames),
  309                    reason="complete native support" if complete else "incomplete interior support")
  310      return reasons(result)
```

## A — `scripts/sample_quiet_predicate_evidence.py:718-887` `collect`

```python
  718  def collect(args, *, clock=None, round_runner=production_round, recorder_factory=PowerRecorder,
  719              metadata_reader=None):
  720      clock = clock or Clock()
  721      out = Path(args.out).resolve()
  722      out.mkdir(parents=True, exist_ok=True)
  723      if any(out.iterdir()):
  724          raise ValueError("collection output directory must be empty; evidence is never overwritten")
  725      raw = out / "raw"
  726      raw.mkdir()
  727      session_id = str(uuid.uuid4())
  728      if metadata_reader is None:
  729          def metadata_reader():
  730              boot = command_text(quiet_admission.BOOT_ARGV)
  731              build = command_text(["/usr/bin/sw_vers", "-buildVersion"])
  732              version = command_text(["/usr/bin/sw_vers"])
  733              executable = Path(pm.POWER_METRICS)
  734              try:
  735                  power_identity = {"path": str(executable), "sha256": hashlib.sha256(executable.read_bytes()).hexdigest()}
  736              except OSError as exc:
  737                  power_identity = {"path": str(executable), "sha256": None, "sha256_reason": str(exc)}
  738              return reasons({"sw_vers": version if isinstance(version, str) else None,
  739                              "powermetrics_identity": power_identity,
  740                              "boot_id": boot if isinstance(boot, str) else None,
  741                              "os_build": build if isinstance(build, str) else None,
  742                              "collector": identity(os.getpid()), "argv": sys.argv,
  743                              "metadata_errors": [v[1] for v in (boot, build) if isinstance(v, tuple)]})
  744      metadata = metadata_reader()
  745      session = {"schema": SCHEMA, "session": session_id, **metadata,
  746                 "state": args.state, "repeat": args.repeat, "load_setting": args.load_cores,
  747                 "duration_s": args.duration_s, "sample_interval_s": args.sample_interval_s,
  748                 "power_interval_ms": args.power_interval_ms, "power_enabled": args.power,
  749                 "powermetrics_needs_root": True, "sudo_policy_probed": False,
  750                 "evidence_status": "PROVISIONAL", "network_time_provenance": None,
  751                 "alignment_model": ALIGNMENT_MODEL,
  752                 "network_time_provenance_reason": "not established by this desk harness",
  753                 "observer_definition": "SELF + reaped CHILDREN over production smoke incl. raw/stamp hooks; recorder CPU excluded",
  754                 "round_workers": [], "power": None, "error": None, "error_rounds": 0}
  755      envelope_cpu_start = cpu_total()
  756      start = clock.stamp()
  757      scheduled = getattr(args, "envelope_start_mono_s", None)
  758      deadline = (start.monotonic_before_s if scheduled is None else scheduled) + args.duration_s
  759      session["scheduled_mono_s"] = scheduled
  760      session["start_drift_s"] = start.monotonic_before_s - scheduled if scheduled is not None else None
  761      session["start_stamp"] = asdict(start)
  762      session["deadline_mono_s"] = deadline
  763      write_json(out / "session.json", session)
  764      recorder = None
  765      rows, frames, anchor = [], [], {"status": "unresolved", "detail": "power disabled"}
  766      try:
  767          if args.power:
  768              path = raw / f"powermetrics-{args.state}-{args.repeat}.plist"
  769              recorder = recorder_factory(path, args.power_interval_ms, clock, deadline)
  770              recorder.start()
  771          while clock.monotonic() < deadline:
  772              index = len(rows) + 1
  773              round_dir = raw / f"round-{index:04d}"
  774              round_dir.mkdir()
  775              before = clock.stamp()
  776              try:
  777                  result = round_runner(args.sample_interval_s, deadline, round_dir, clock)
  778              except (Exception, KeyboardInterrupt) as exc:
  779                  session["error"] = f"{type(exc).__name__}: {exc}"
  780                  result = {"status": "partial" if isinstance(exc, KeyboardInterrupt) else "error",
  781                            "error": session["error"], "observation": None, "observer_cpu_s": None,
  782                            "end_stamp": asdict(clock.stamp())}
  783              after = ClockStamp(**result["end_stamp"])
  784              row = new_row(session_id, args, index, before, after, result)
  785              if result.get("cleanup_incomplete"):
  786                  session["error"] = "round worker cleanup incomplete; collection stopped"
  787              if after.monotonic_after_s > deadline:
  788                  # Support ends at the duration limit, not after child cleanup.
  789                  offset = after.monotonic_after_s - deadline
  790                  row["round_wall_end_s"] = after.epoch_s - offset
  791                  row["round_mono_end_s"] = deadline
  792                  row["alignment"]["end_clipping_s"] = offset
  793                  row["status"] = "partial"
  794                  row["error"] = row["error"] or "round exceeded collection duration"
  795              row["boot_id"] = metadata.get("boot_id")
  796              row["os_build"], build_error = os_build_identity(session.get("os_build"))
  797              row["os_build_valid"] = build_error is None
  798              if build_error is not None:
  799                  row["os_build_reason"] = build_error
  800              session["round_workers"].append({"round": index, "workers": result.get("workers", []),
  801                                               "argv": result.get("argv", []),
  802                                               "identities": [json.loads(p.read_text()) for p in sorted(round_dir.glob("*-identity.json"))]})
  803              sampler = round_dir / "sampler.json"
  804              if sampler.exists():
  805                  evidence = json.loads(sampler.read_text())
  806                  row["alignment"].update(evidence["marks"])
  807                  row["alignment"]["sampler_wall_stamps"] = evidence["wall_reads"]
  808                  ps_start, ps_end = (evidence["marks"].get(k) for k in ("ps_start", "ps_end"))
  809                  if ps_start is not None and ps_end is not None:
  810                      row["alignment"]["ps_span_s"] = ps_end - ps_start
  811                      row["alignment"]["round_minus_ps_s"] = row["round_mono_end_s"] - row["round_mono_start_s"] - (ps_end - ps_start)
  812                      top_start, top_end = (evidence["marks"].get(k) for k in ("top_start", "top_end"))
  813                      top_span = top_end - top_start if top_start is not None and top_end is not None else None
  814                      row["alignment"].update(top_command_span_s=top_span,
  815                          ps_top_span_mismatch=(abs(ps_end - ps_start - top_span) > 1e-6) if top_span is not None else None,
  816                          round_ps_span_mismatch=abs(row["alignment"]["round_minus_ps_s"]) > 1e-6)
  817              rows.append(row)
  818              # Durable one-row-per-attempt journal before the offline reduction.
  819              with (out / "rounds.jsonl").open("a") as stream:
  820                  stream.write(json.dumps(reasons(row, "power reduction pending or source unavailable"), allow_nan=False) + "\n")
  821                  stream.flush()
  822                  os.fsync(stream.fileno())
  823              if row["status"] == "partial" or session["error"]:
  824                  break
  825              if clock.monotonic() <= before.monotonic_before_s:
  826                  raise RuntimeError("round made no monotonic progress")
  827      except (Exception, KeyboardInterrupt) as exc:
  828          session["error"] = f"{type(exc).__name__}: {exc}"
  829      finally:
  830          if recorder is not None:
  831              try:
  832                  frames, anchor = recorder.finish()
  833              except Exception as exc:
  834                  session["error"] = (session["error"] or "") + f"; power finalization: {exc}"
  835                  anchor = {"status": "unresolved", "detail": str(exc)}
  836              session["power"] = recorder.metadata
  837              cleanup = recorder.metadata.get("cleanup") or {}
  838              if cleanup.get("kill") or (cleanup and cleanup.get("returncode") is None):
  839                  session["error"] = (session["error"] or "") + "; power cleanup escalated; root descendant termination needs bench verification"
  840              elif cleanup and cleanup["returncode"] not in (0, -signal.SIGTERM, 128 + signal.SIGTERM):
  841                  session["error"] = (session["error"] or "") + f"; powermetrics exit {cleanup['returncode']}"
  842          session["end_stamp"] = asdict(clock.stamp())
  843          session["whole_envelope_observer_cpu_s"] = cpu_total() - envelope_cpu_start
  844          session["whole_envelope_observer_definition"] = "SELF + all reaped CHILDREN, including power recorder; never subtracted"
  845      session["error_rounds"] = sum(row["status"] == "error" for row in rows)
  846      if session["error_rounds"] and not any(row["status"] == "complete" for row in rows):
  847          session["error"] = session["error"] or "no round completed successfully"
  848      if getattr(args, "interior_s", None) is not None:
  849          interior_anchor = dict(anchor)
  850          if anchor.get("status") == "bounded":
  851              interior_anchor["effective_clock_anchor_bound_s"] += start.monotonic_after_s - start.monotonic_before_s
  852          # Use the wall/monotonic mapping in the actual start bracket to map
  853          # the frozen scheduled start, preserving the bracket uncertainty.
  854          interior_epoch = start.epoch_s - (session["start_drift_s"] or 0) + args.interior_offset_s
  855          session["interior"] = reduce_interior(frames, interior_anchor, interior_epoch, args.interior_s)
  856      for row in rows:
  857          align = row["alignment"]
  858          why = str(anchor.get("detail", anchor.get("reason", "clock anchor unresolved")))
  859          if anchor["status"] == "bounded" and row["round_wall_end_s"] > row["round_wall_start_s"]:
  860              epsilon = anchor["effective_clock_anchor_bound_s"]
  861              # Add this round's own wall-read brackets to the production bound.
  862              epsilon += max(s["monotonic_after_s"] - s["monotonic_before_s"]
  863                             for s in (align["round_start_stamp"], align["round_end_stamp"]))
  864              values = integrate(frames, row["round_wall_start_s"], row["round_wall_end_s"], epsilon)
  865              row.update({k: values[k] for k in ("power", "clusters", "cpus")})
  866              align.update(anchor_lo=anchor["admissible_lower_epoch_s"], anchor_hi=anchor["admissible_upper_epoch_s"],
  867                           error_bound_j=values["error_bound_j"], rail_error_bound_j=values["rail_error_bound_j"],
  868                           frame_span_mismatch=values["span_mismatch"], error_bound_s=epsilon,
  869                           error_bound_j_reason="incomplete rail coverage; unobserved energy is unbounded")
  870          else:
  871              align.update(frame_span_mismatch=True, error_bound_j_reason=why)
  872              row["power"] = reasons(row["power"], why)
  873          align.update(method=anchor.get("method"), anchor_status=anchor["status"],
  874                       model=ALIGNMENT_MODEL,
  875                       bound_method="sum of per-frame overlap perturbation bounds on the interval-average power signal; gaps unbounded")
  876          if align["error_bound_j"] is not None:
  877              align.pop("error_bound_j_reason", None)
  878          paths = sorted(p for p in raw.rglob("*") if p.is_file() and (
  879              p.parent == raw or p.parent.name == f"round-{row['round']:04d}"))
  880          row["raw"] = {"paths": [str(p.relative_to(out)) for p in paths],
  881                        "sha256": {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
  882      # Final reduction replaces only this session's provisional derived journal.
  883      with (out / "rounds.jsonl").open("w") as stream:
  884          for row in rows:
  885              stream.write(json.dumps(reasons(row), sort_keys=True, allow_nan=False) + "\n")
  886      write_json(out / "session.json", session)
  887      return session, rows
```

## A — `joulewise/night_gate.py:53-60` `RULED_REGISTRATIONS`

```python
   53  RULED_REGISTRATIONS = {
   54      D166_REGISTRATION_SHA256: {"label": "D-166 dominance criterion", "ruling": "D-165/D-166", "binds_chain": False,
   55          "records": ("docs/decision_log.md#D-165", "docs/decision_log.md#D-166")},
   56      QPE01_PILOT_REGISTRATION_SHA256: {"label": "QPE-01 idle-variance pilot protocol v1",
   57          "ruling": "cold gate 10 Q1/Q2 (2026-09-19); sizing ruling 46b", "binds_chain": True,
   58          "records": ("docs/process_traces/2026-09-19-activation-d0b83820/10-coldgate-packet-stage-a-executor/10-coldgate-fable-ruling.md",
   59                      "docs/process_traces/2026-09-19-activation-d0b83820/46b-ruling-stage-a-seat-r3.md")},
   60  }
```

