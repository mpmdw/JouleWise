import collections, json, os, sys

STATUSES = {"succeeded", "failed", "unsupported"}                      # joulewise/schemas.py:233-236
REASONS = {"did_not_fit", "runtime_unavailable", "model_identity_mismatch", "telemetry_unavailable",
           "format_unavailable", "permission_denied", "transport_unavailable", "unsupported_workload",
           "cleanup_failed", "unknown_error"}                           # joulewise/schemas.py:267-277
PHASES = {"validate", "prepare", "idle_baseline", "warmup", "measured_run",
          "idle_drift_sentinel", "cleanup", "reduce"}                  # controller._begin_stage call sites
CONDITIONS = {"cpu_baseline_telemetry_missing", "cpu_baseline_telemetry_malformed",
              "cpu_baseline_sample_count_insufficient", "cpu_busy_ratio_p95_exceeded",
              "processor_combined_power_w_p95_exceeded", "gpu_idle_admission_not_passed",
              "gpu_idle_admission_unknown"}                            # joulewise/idle_admission.py:44-50
DECISIONS = {"admitted", "abort"}

def load(path):
    try:
        with open(path, "rb") as handle:
            value = json.loads(handle.read())
        return value if isinstance(value, dict) else None
    except (OSError, ValueError):
        return None

def name(value, allowed):
    return value if isinstance(value, str) and value in allowed else "other"

def intervals_of(journal_path):
    rows = []
    with open(journal_path, "rb") as handle:
        for line in handle:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if not isinstance(row, dict) or row.get("kind") != "interval":
                continue
            values = row.get("values") if isinstance(row.get("values"), dict) else {}
            wall = (values.get("interval") or {}).get("wall_ns")
            names = sorted({o.get("command") for o in (values.get("outside_over_limit") or [])
                            if isinstance(o, dict) and isinstance(o.get("command"), str)})
            if isinstance(wall, list) and len(wall) == 2 and names:
                rows.append((wall[0] / 1e9, wall[1] / 1e9, names))
    return rows

try:
    bound_root, claim_root, journal_path = sys.argv[1:4]
    dirty = intervals_of(journal_path)
    span = (min(s for s, _, _ in dirty), max(e for _, e, _ in dirty)) if dirty else None
    for label, root in (("bound", bound_root), ("claim", claim_root)):
        tally = collections.Counter()
        clock_ok = clock_bad = 0
        for entry in sorted(os.listdir(root)):
            bundle = os.path.join(root, entry)
            summary = load(os.path.join(bundle, "summary_metrics.json"))
            metadata = load(os.path.join(bundle, "metadata.json"))
            if summary is None and metadata is None:
                continue
            tally["bundles"] += 1
            status = name(summary.get("status") if summary else None, STATUSES)
            tally["status." + status] += 1
            succeeded = status == "succeeded"
            admission = metadata.get("environment_admission") if metadata else None
            attempts = admission.get("attempts") if isinstance(admission, dict) else None
            attempts = [a for a in attempts if isinstance(a, dict)] if isinstance(attempts, list) else []
            # Join: did any idle-baseline attempt overlap a dirty journal interval?
            windows = [(a.get("start_s"), a.get("end_s")) for a in attempts]
            windows = [(s, e) for s, e in windows if isinstance(s, (int, float)) and isinstance(e, (int, float))]
            group = "succeeded" if succeeded else "not_succeeded"
            if not windows:
                tally["join." + group + ".baseline_times_absent"] += 1
            else:
                for s, e in windows:
                    if span and span[0] - 3600 <= s <= span[1] + 3600:
                        clock_ok += 1
                    else:
                        clock_bad += 1
                hit = set()
                for s, e in windows:
                    for ds, de, names in dirty:
                        if ds < e and de > s:
                            hit.update(names)
                tally["join." + group + (".baseline_overlaps_over_limit" if hit else ".baseline_clean")] += 1
                if not succeeded:
                    for process in hit:
                        tally["join.offenders_in_not_succeeded_baselines." + process] += 1
            if succeeded:
                continue
            tally["failure_reason." + name(summary.get("failure_reason") if summary else None, REASONS)] += 1
            try:
                with open(os.path.join(bundle, "events.jsonl"), "rb") as handle:
                    for line in handle:
                        try:
                            event = json.loads(line)
                        except ValueError:
                            continue
                        if isinstance(event, dict) and event.get("event_type") == "failure":
                            tally["failure_phase." + name(event.get("phase"), PHASES)] += 1
            except OSError:
                tally["failure_phase.events_unreadable"] += 1
            if not isinstance(admission, dict):
                tally["admission.record_absent"] += 1
                continue
            tally["admission.decision." + name(admission.get("decision"), DECISIONS)] += 1
            tally["admission.attempts." + (str(len(attempts)) if len(attempts) <= 2 else "more")] += 1
            for ordinal, attempt in enumerate(attempts[:2], 1):
                cpu = attempt.get("cpu_admission") if isinstance(attempt.get("cpu_admission"), dict) else {}
                codes = cpu.get("conditions") if isinstance(cpu.get("conditions"), list) else []
                for code in sorted(set(codes) & CONDITIONS):
                    tally["admission.attempt%d.%s" % (ordinal, code)] += 1
                if not codes:
                    tally["admission.attempt%d.no_condition" % ordinal] += 1
        tally["join.clock_check." + ("ok" if clock_bad == 0 else "mismatch")] = 1
        for key, count in sorted(tally.items()):
            print("%s.%s %d" % (label, key, count))
except Exception:
    print("probe.failed 1")
