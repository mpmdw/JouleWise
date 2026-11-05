"""Synthetic old-format GO records for historical lineage reader fixtures."""
from __future__ import annotations
from types import FunctionType

def _prepare_pack_night(plan: NightPlan, plan_path: Path, plan_raw: bytes):
    """Re-read pinned plan and authority before authoring ARM or publishing GO."""
    _pack_bytes(plan_path, "plan_sha256", hashlib.sha256(plan_raw).hexdigest())
    return night_gate._authenticate_pack_records(plan)


def _pack_launch_references(plan: NightPlan, arm):
    root = Path(plan.pack_night["pack_root"])
    pack_custody = Path(plan.custody_root) / plan.pack_night["pack_id"]
    fixed = pack_custody / "arm_readiness.t0.inputs/launch-manifest.json"
    _pack_bytes(fixed, "launch_manifest")
    # More than one manifest-shaped input is ambiguous even if one has the
    # preferred spelling. Never choose a fallback candidate.
    for path in (pack_custody / "arm_readiness.t0.inputs").rglob("*.json"):
        if path != fixed and _pack_object(path, "launch_manifest candidates").get("schema_version") == readiness.LAUNCH_MANIFEST_SCHEMA:
            raise PackNightRefusal("launch_manifest: duplicate candidate")
    refs = readiness._attested_launch_artifact_references(root, pack_custody, arm, launch_binding_cache={})
    if refs["launch_manifest"]["path"] != str(fixed):
        raise PackNightRefusal("launch_manifest.path")
    for name, item in refs.items():
        _pack_bytes(Path(item["path"]), name + "_sha256", item["sha256"])
    if refs["window_chain"]["path"] != plan.chain_path:
        raise PackNightRefusal("window_chain.path")
    return refs


def _produce_pack_go(plan, plan_path, plan_raw, prepared, arm_state, receipt, probes):
    """Final producer reauthentication; publish once only after every check."""
    if receipt.verdict != "GO" or any(row.status != "PASS" for row in receipt.conditions):
        raise PackNightRefusal("conditions: refused night")
    current = _prepare_pack_night(plan, plan_path, plan_raw)
    if current != prepared:
        raise PackNightRefusal("preparation changed")
    arm = arm_state["arm"]
    night_gate.authenticate_arm_context(plan, arm["arm_context"],
        legacy_rehearsal=prepared["authorization_record"]["purpose"] == "T0_REHEARSAL")
    _pack_digest(plan, arm)
    confirmation = prepared["confirmation_record"]
    readiness._verify_arm_receipt(prepared["root"], arm_state["path"], require_unconsumed=True,
        step6_confirmation_table=confirmation["table_path"], expected_confirmation_digest=confirmation["table_sha256"])
    _pack_bytes(arm_state["path"], "arm_receipt", arm_state["sha256"])
    _pack_no_retry(plan, readiness._current_boot_session_id(), arm_state["path"])
    refs = _pack_launch_references(plan, arm)
    evidence = _pack_evidence(plan, arm_state)
    probe, refusal = agent_census(probes)
    _append_census(Path(plan.custody_root) / "night/censuses.jsonl", probe, refusal)
    if refusal is not None or probe.exit_code != 1 or probe.stdout != "":
        raise PackNightRefusal("census: " + (refusal.detail if refusal else "stdout must be empty"))
    issued = time.monotonic_ns()
    issued_epoch = float(probes.now_epoch_s())
    if not plan.t0_epoch_s <= issued_epoch <= plan.t0_epoch_s + plan.window_max_s:
        raise PackNightRefusal("conditions.C5.window_expired")
    if arm["boot_session_id"] != readiness._current_boot_session_id() or not probe.monotonic_ns <= issued < arm["valid_until_monotonic_ns"]:
        raise PackNightRefusal("boot_session_id/valid_until_monotonic_ns")
    authorization = prepared["authorization_record"]
    calibration_plan_id = (readiness._pack_record(prepared["root"])["plan_id"]
                           if plan.previous_attempt is not None else plan.plan_id)
    if arm["pack"]["plan_id"] != calibration_plan_id:
        raise PackNightRefusal("arm_receipt.pack.plan_id")
    if arm["reviewed_main"]["head_commit"] != plan.repo_head or probes.checkout_head() != plan.repo_head:
        raise PackNightRefusal("repo_head")
    if next(row for row in receipt.conditions if row.condition_id == "C4").measured.get("boot_session_uuid") != arm["boot_session_id"]:
        raise PackNightRefusal("conditions.C4.boot_session_id")
    _pack_rehearsal_roots(plan, arm, authorization["purpose"])
    custody = Path(plan.custody_root).resolve(strict=True)
    def reference(path, digest):
        return {"path": Path(path).resolve(strict=True).relative_to(custody).as_posix(), "sha256": digest}
    arm_ref = reference(arm_state["path"], arm_state["sha256"])
    auth_ref = reference(plan.pack_night["authorization_record"]["path"], plan.pack_night["authorization_record"]["sha256"])
    confirmation_ref = reference(plan.pack_night["confirmation_record"]["path"], plan.pack_night["confirmation_record"]["sha256"])
    # The running census journal remains append-only. GO instead binds this
    # immutable snapshot so a later journal append cannot invalidate C3 replay.
    census_path = custody / "night/go-census.json"
    census_raw = readiness.render_json(_census_record(probe, None))
    _write_bytes_exclusive(census_path, census_raw)
    census_ref = reference(census_path, readiness.sha256_bytes(census_raw))
    condition_evidence = {"C1": [auth_ref, confirmation_ref], "C2": [arm_ref, *evidence],
                          "C3": [census_ref], "C4": evidence, "C5": [arm_ref, auth_ref]}
    conditions = []
    for row in receipt.conditions:
        conditions.append({"condition_id": row.condition_id, "status": row.status, "basis": row.basis,
                           "evidence": condition_evidence[row.condition_id], "measured": dict(row.measured)})
    go = {
        "schema_version": "joulewise.pack_night_go_receipt.v1", "receipt_id": str(uuid.uuid4()),
        "receipt_class": "TRANSACTION_PACK", "purpose": authorization["purpose"],
        "plan_id": plan.plan_id, "plan_sha256": readiness.sha256_bytes(plan_raw),
        "pack_id": plan.pack_night["pack_id"], "pack_sha256": plan.pack_night["pack_sha256"],
        "arm_receipt": {"receipt_id": arm["receipt_id"], "sha256": arm_state["sha256"],
                        "valid_until_monotonic_ns": arm["valid_until_monotonic_ns"]},
        "boot_session_id": arm["boot_session_id"], "t0_evidence": evidence,
        "t0_evidence_set_sha256": readiness.sha256_bytes(readiness.render_json(evidence)),
        "launch_manifest_sha256": refs["launch_manifest"]["sha256"],
        "window_environment_sha256": refs["window_environment"]["sha256"],
        "window_chain_sha256": refs["window_chain"]["sha256"],
        "repo_head": plan.repo_head, "measurement_root": plan.measurement_root, "measurement_head": plan.measurement_head,
        "confirmation_record": dict(plan.pack_night["confirmation_record"]),
        "authorization": {**plan.pack_night["authorization_record"], **{k: authorization[k] for k in ("purpose", "attempt_id", "claim_eligible")}},
        "census": {"argv": list(probe.argv), "exit_code": probe.exit_code,
                   "stdout_sha256": readiness.sha256_bytes(probe.stdout.encode()), "monotonic_ns": probe.monotonic_ns},
        "issued_epoch_s": issued_epoch, "issued_monotonic_ns": issued,
        "valid_until_monotonic_ns": arm["valid_until_monotonic_ns"], "conditions": conditions, "verdict": "GO",
    }
    path = Path(plan.custody_root) / "night/go_receipt.json"
    _write_bytes_exclusive(path, readiness.render_json(go))
    _fsync_path(path.parent)
    return (_pack_launcher_argv(plan, plan_path, arm_state["path"], Path(refs["launch_manifest"]["path"]), path, confirmation),
            {"ARM_RECEIPT": str(arm_state["path"]), "LAUNCH_MANIFEST": str(refs["launch_manifest"]["path"])})


def _pack_launcher_argv(plan, plan_path, arm_path, manifest_path, go_path, confirmation):
    return [str(Path(plan.measurement_root) / ".venv/bin/python"),
            str(Path(plan.measurement_root) / "scripts/launch_window.py"),
            "--pack-root", plan.pack_night["pack_root"], "--arm-receipt", str(arm_path),
            "--arm-readiness-custody-root", plan.custody_root, "--launch-manifest", str(manifest_path),
            "--night-plan", str(plan_path), "--go-receipt", str(go_path),
            "--step6-confirmation-table", confirmation["table_path"],
            "--expected-confirmation-digest", confirmation["table_sha256"]]

_originals = {name: value for name, value in list(globals().items())
              if callable(value) and getattr(value, "__module__", None) == __name__}

def produce(driver, *args, **kwargs):
    namespace = dict(vars(driver))
    from joulewise import receipt_formats
    namespace["t0_author"] = receipt_formats
    for name, original in _originals.items():
        namespace[name] = FunctionType(original.__code__, namespace, name,
                                       original.__defaults__, original.__closure__)
        namespace[name].__kwdefaults__ = original.__kwdefaults__
    return namespace["_produce_pack_go"](*args, **kwargs)

def prepare(driver, *args, **kwargs):
    namespace = dict(vars(driver))
    function = _originals["_prepare_pack_night"]
    return FunctionType(function.__code__, namespace, function.__name__,
                        function.__defaults__)(*args, **kwargs)
