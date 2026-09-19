# Exhibit A — the code the question turns on (verbatim `sed` extracts at main `0c529f99`)

## joulewise/night_gate.py lines 30,50 at main `0c529f99`

```
RECEIPT_CLASSES = (
    "DIAGNOSTIC_NO_PACK",
    "REHEARSAL_STUB",
    "TRANSACTION_PACK",
)
# 2026-09-05: D-165 v2 relabel supersedes the v1 registration digest
# 1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b (bytes retained in Git history).
D166_REGISTRATION_SHA256 = (
    "dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265"
)
# Tracked file whose bytes are canonical_json_bytes(dominance_criterion_registration());
# a night plan's registration_path points at it (repo-relative or absolute).
D166_REGISTRATION_PATH = (
    "configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json"
)
AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-lf", "codex|claude|t3")

PMSET_BATT_ARGV = ("/usr/bin/pmset", "-g", "batt")
PMSET_GENERAL_ARGV = ("/usr/bin/pmset", "-g")
HID_IDLE_ARGV = (
    "/usr/bin/defaults",
```

## joulewise/night_gate.py lines 460,476 at main `0c529f99`

```
    """Return the ruled target status and registered basis for each class.

    ``PASS`` is a requirement, so a well-formed refusal may carry ``FAIL`` in
    that row.  ``NOT_APPLICABLE`` is an exact status/basis pair.
    """

    return {
        "DIAGNOSTIC_NO_PACK": {
            "C1": ("PASS", None),
            "C2": ("NOT_APPLICABLE", "no_pack_by_design"),
            "C3": ("PASS", None),
            "C4": ("PASS", None),
            "C5": ("PASS", None),
        },
        "REHEARSAL_STUB": {
            "C1": ("PASS", None),
            "C2": ("NOT_APPLICABLE", "no_pack_by_design"),
```

## joulewise/night_gate.py lines 1325,1360 at main `0c529f99`

```
        "boot_session_uuid": canonical_uuid,
        "clock_epoch_s": clock_epoch_s,
        "clock_monotonic_ns": clock_monotonic_ns,
    }
    rows["C4"].evidence.append("clock:epoch+monotonic")


def _check_registration(plan, probes, rows, evidence):
    clock_monotonic_ns = rows["C4"].measured.get("clock_monotonic_ns")
    if plan.receipt_class in {"DIAGNOSTIC_NO_PACK", "REHEARSAL_STUB"}:
        try:
            registration_text = probes.read_text(plan.registration_path)
            if not isinstance(registration_text, str):
                raise ProbeError("registration probe must return text")
            registration_sha256 = hashlib.sha256(
                registration_text.encode("utf-8")
            ).hexdigest()
        except Exception as exc:
            return _probe_refusal(plan, probes, rows, evidence, exc)
        rows["C1"].evidence.append(f"registration:{plan.registration_path}")
        rows["C1"].measured = {
            "registration_path": plan.registration_path,
            "registration_sha256": registration_sha256,
        }
        if registration_sha256 != D166_REGISTRATION_SHA256:
            return _finish(
                plan,
                probes,
                rows,
                Refusal(
                    "night_refused_registration",
                    f"registration sha256 {registration_sha256} does not match D-166 registration",
                    tuple(evidence),
                ),
                authored_monotonic_ns=clock_monotonic_ns,
            )
```

## joulewise/night_gate.py lines 1210,1250 at main `0c529f99`

```
                rows,
                Refusal(
                    "night_refused_not_quiet",
                    "displaysleep predicate failed",
                    tuple(evidence),
                ),
            )

        if legacy_load:
            load = _run(probes, LOAD_AVG_ARGV)
            evidence.append(load)
            rows["C3"].evidence.append(_probe_citation(load))
            rows["C3"].measured["load_average_raw"] = load.stdout
            load_match = _LOAD_AVG_RE.fullmatch(load.stdout.strip())
            if not _completed_ok(load) or load_match is None:
                raise ProbeError(
                    "load average output malformed: "
                    f"exit={load.exit_code}, stdout={load.stdout[:200]!r}"
                )
            load_1m = float(load_match.group(1))
            rows["C3"].measured["load_1m"] = load_1m
            if load_1m > LOAD_MAX:
                return _finish(
                    plan,
                    probes,
                    rows,
                    Refusal(
                        "night_refused_not_quiet",
                        f"load_average predicate failed (maximum {LOAD_MAX})",
                        tuple(evidence),
                    ),
                )

        thermal = _run(probes, THERMAL_ARGV)
        evidence.append(thermal)
        rows["C3"].evidence.append(_probe_citation(thermal))
        rows["C3"].measured["thermal_raw"] = thermal.stdout
        thermal_limits: list[str] = []
        for thermal_line in thermal.stdout.splitlines():
            stripped_line = thermal_line.strip()
            if not stripped_line.startswith("CPU_Speed_Limit"):
```

## joulewise/night_agent_install.py lines 745,800 at main `0c529f99`

```
            continue
        if isinstance(record, dict) and record.get("event") in final_events:
            rows += 1
    return rows


def probe_bindings(plan, plan_path, python):
    """Bind the actual reservation inputs and the effective interpreters."""
    chain = Path(plan.chain_path)
    digest = _digest(chain)
    sidecar = Path(plan.chain_sha256_path).read_text().split()
    if (not sidecar or sidecar[0] != digest or len(sidecar) > 2
            or (len(sidecar) == 2 and sidecar[1] != chain.name)):
        raise ValueError("chain_sha256 mismatch")
    paths = chain_literal_paths(chain)
    pin = json.loads(paths["LEDGER_HEAD_PIN"].read_text())
    head = pin["head_digest"]
    rows = paths["CALIBRATION_LEDGER"].read_text().splitlines()
    physical = json.loads(rows[-1])["receipt_digest"] if rows else "0" * 64
    if not re.fullmatch(r"[0-9a-f]{64}", head) or physical != head:
        raise ValueError("ledger_head_sha256 mismatch")
    root = Path(plan.measurement_root)
    source = root / "scripts/night_chains/calibration_derivation_only.zsh"
    if "NIGHT_VERIFY_ONLY" not in source.read_text() or "calibration_derivation_only.zsh" not in chain.read_text():
        raise ValueError("chain does not support reservation verify-only mode")
    if "NIGHT_RESERVATION_ARGV_ONLY" not in source.read_text():
        raise ValueError("input_digests: chain lacks reservation argument inspection")
    inputs = reservation_input_digests(plan, plan_path)
    return {"plan_id": plan.plan_id, "plan_sha256": _digest(plan_path),
            "input_digests": inputs,
            "measurement_head": plan.measurement_head, "ledger_head_sha256": head,
            "custody_budget_s": float(getattr(plan, "custody_budget_s", 120)),
            "code_digests": {name: "sha256:" + _digest(root / name) for name in PROBE_CODE_PATHS},
            "driver_python": interpreter_identity(python),
            "chain_python": interpreter_identity(root / ".venv/bin/python"),
            "chain_sha256": digest, "chain_source_sha256": _digest(source),
            # Bind ledger bytes as well as the head; never trust a copied tail.
            "ledger_sha256": _digest(paths["CALIBRATION_LEDGER"]),
            "ledger_pin_sha256": _digest(paths["LEDGER_HEAD_PIN"])}


def probe_label(plan_id):
    label = "com.joulewise.night-probe." + plan_id
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", label):
        raise Refused(2, "probe plan_id is not a valid launchd label")
    return label


def validate_probe_receipt(prepared, max_age_s=PROBE_RECEIPT_MAX_AGE_S, receipt_path=None):
    import math
    path = receipt_path or prepared.plan_path.parent / "night_probe_receipt.json"
    try:
        receipt = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise Refused(2, "probe receipt missing or invalid: {}: {}".format(path, exc))
    if not isinstance(receipt, dict) or receipt.get("schema") != "joulewise.night_probe_receipt.v1":
```

## scripts/run_night.py lines 3255,3275 at main `0c529f99`

```
        elif not gone:
            record.update(outcome="refused", refusal_code="probe_process_survived")
        elif not output.is_file():
            record.update(outcome="refused", refusal_code="probe_worker_failed", detail=stderr.decode(errors="replace"))
        _atomic_probe_json(receipt_path, record)
    return 0 if record["outcome"] == "ok" else 2


def _probe_worker(plan_path: Path, receipt_path: Path, progress_path: Path, deadline: float) -> int:
    """Disposable worker; the supervisor bounds every synchronous read below."""
    import tempfile
    from joulewise.night_agent_install import interpreter_identity, probe_bindings

    def phase(name, record=None):
        _atomic_probe_json(progress_path, {"phase": name, "record": record or {}})
    phase("plan")
    started = time.time()
    plan = _load_plan(plan_path)
    phase("bindings", {"plan_id": plan.plan_id, "measurement_head": plan.measurement_head})
    bindings = probe_bindings(plan, plan_path, sys.executable)
    record = dict(bindings, schema="joulewise.night_probe_receipt.v1",
```

## scripts/run_night.py lines 875,910 at main `0c529f99`

```
                census_count,
                census_hits,
                bool(outcome["proven"]),
            )

        next_census = time.monotonic()
        while process.poll() is None:
            now = time.monotonic()
            # Three checks, because the two calls between them can each block
            # without bound: the census probe and the census append. The
            # watchdog thread covers a block that never returns at all; these
            # keep the ordinary path from spending a whole probe timeout or
            # census interval past the deadline.
            if deadline.expired():
                fired = deadline.fire()
                if fired is not None:
                    return exceeded(fired)
            if now >= next_census:
                probe, refusal = agent_census(probes)
                if deadline.expired():
                    fired = deadline.fire()
                    if fired is not None:
                        return exceeded(fired)
                record = _census_record(probe, refusal)
                _append_census(census_path, probe, refusal)
                census_count += 1
                if deadline.expired():
                    fired = deadline.fire()
                    if fired is not None:
                        return exceeded(fired)
                if refusal is not None:
                    census_hits.append(record)
                    if abort_on_census:
                        # The wall-clock stop wins if it already fired: the
                        # group is gone and the exit is recorded.
                        fired = deadline.cancel()
```

## joulewise/quiet_admission.py lines 155,180 at main `0c529f99`

```
                              command=row["command"], busy_cores=delta / interval_s,
                              observer=row["pid"] in observers))
    process_busy = sum(item["busy_cores"] for item in consumers)
    host_busy = logical_cpu * (1 - idle_fraction)
    return dict(process_busy_cores=process_busy, host_busy_cores=host_busy,
                busy_cores=max(process_busy, host_busy), logical_cpu=logical_cpu,
                idle_fraction=idle_fraction, unaccounted=unaccounted,
                top_consumers=sorted(consumers, key=lambda item: (-item["busy_cores"], item["pid"]))[:10])


def is_quiet(metrics, policy):
    busy = metrics["busy_cores"]
    if isinstance(busy, bool) or not isinstance(busy, (int, float)) or not math.isfinite(busy) or busy < 0:
        raise ValueError("invalid busy_cores")
    # Zero is the explicitly non-admitting validation-fixture sentinel.
    return policy["busy_core_max"] > 0 and busy <= policy["busy_core_max"]


def validate_observation(value, policy, *, allow_unavailable_boot=False):
    """Reject missing or non-finite worker evidence before it can be quiet."""
    required = {"wall_start", "wall_end", "monotonic_start", "monotonic_end", "interval_s",
                "boot_identity", "raw_sha256", "metrics", "load_avg_diagnostic",
                "census"}
    if isinstance(value, dict) and "boot_identity_unavailable" in value:
        reason = value["boot_identity_unavailable"]
        if not isinstance(reason, str) or not reason.strip() or value.get("boot_identity") is not None:
```

## scripts/gen_derivation_night.py lines 475,505 at main `0c529f99`

```
        raise GenerationRefusal(f"night plan is not an exact {version} plan: {error}") from error
    # An allow-list, not a pack-only refusal: TRANSACTION_PACK launches a pack
    # launcher instead of the plan's chain and REHEARSAL_STUB never runs the
    # chain at all, so a wrapper emitted for either would never execute.
    if plan.receipt_class != DERIVATION_RECEIPT_CLASS:
        raise GenerationRefusal(
            f"a derivation night is {DERIVATION_RECEIPT_CLASS}; this plan is "
            f"{plan.receipt_class}"
        )

    slot_count = args.slot_count
    if slot_count != PRE_REGISTERED_SLOT_COUNT and not args.allow_slot_count:
        raise GenerationRefusal(
            f"slot count {slot_count} is not the pre-registered "
            f"{PRE_REGISTERED_SLOT_COUNT}; pass --allow-slot-count with "
            "--slot-count-ruling <ref> to override"
        )
    if slot_count != PRE_REGISTERED_SLOT_COUNT:
        if not args.slot_count_ruling:
            raise GenerationRefusal(
                "--allow-slot-count requires --slot-count-ruling <ref>: departing "
                f"from the pre-registered {PRE_REGISTERED_SLOT_COUNT} slots needs "
                "a named authority, and the reference is written into the wrapper"
            )
        _validated_ruling(args.slot_count_ruling)
    if slot_count < 1:
        raise GenerationRefusal("slot count must be positive")
    # The ledger refuses a declared-slot list longer than this, and it refuses
    # it INSIDE the window, at the reservation, with the night already spent.
    if slot_count > MAX_DECLARED_SESSION_SLOTS:
        raise GenerationRefusal(
```

