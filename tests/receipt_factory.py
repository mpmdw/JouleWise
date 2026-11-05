"""Synthetic historical receipt issuers for reader tests only.

Copied from the pre-prune implementation. Production exposes readers only.
Each invocation resolves reader helpers afresh so existing fixture patches keep
working; this module has no production importers or command entry point.
"""
from __future__ import annotations
from functools import wraps
from types import FunctionType
from joulewise import receipt_readers as _readers
globals().update({k: v for k, v in vars(_readers).items() if not k.startswith("__")})


def generate_freeze_receipt(
    pack_root: Path | str,
    *,
    measurement_checkout: Path | str,
    predecessor_pack_root: Path | str | None = None,
    family_publication_marker: Path | str | None = None,
    step6_confirmation_table: Path | str | None = None,
    expected_confirmation_digest: str | None = None,
) -> dict[str, Any]:
    """Write or idempotently authenticate the pack's non-authorizing receipt.

    ``measurement_checkout`` is the operator's required absolute declaration,
    not a receipt field.  When a new receipt is minted, the repository that
    owns ``pack_root`` must resolve exactly to it before any receipt is written.
    An idempotent replay does not re-apply this mint-only gate.  No environment
    variable, current-working-directory default, or pack-derived fallback is
    consulted.

    A successor pack (family generation two or later) must present the path of
    its predecessor pack.  Every ID, digest, ordinal, and conclusion in the
    resulting ``predecessor`` binding is derived here from committed bytes; the
    caller supplies paths only.

    During the intended `_v5` ordering the successor histsem pinset does not
    exist at freeze time, so there is no digest-conditional changed path to
    subtract and an absent confirmation digest is harmless.  Once that pinset
    exists, the same replay path requires both the table and its out-of-band
    expected digest and fails closed without them.
    """

    root = Path(pack_root).resolve(strict=True)
    try:
        if predecessor_pack_root is not None:
            _gate_receipt_histsem(Path(predecessor_pack_root))
    except HistoricalSemanticsError as exc:
        return {
            "status": "REFUSE",
            "arm_disposition": "NOT_APPLICABLE",
            "receipt_path": None,
            "receipt_sha256": None,
            "reason_codes": [exc.reason_code],
            "detail": str(exc),
            "mutated": False,
        }
    registry, _registry_raw, registry_reference = _registry_reference(root)
    tree, _tree_raw = _plan_tree(root)
    attachments = tree.get("arm_attachments")
    readiness = attachments.get("arm_readiness") if isinstance(attachments, Mapping) else None
    _valid_plan_attachment(readiness, registry_reference)
    generation = _pack_generation(root.name)
    # Split S-2: engage on the REGISTRY's mandatory generation threshold.  A
    # threshold-less registry is invalid at load time, so freeze can never skip
    # publication through a dormant configuration.
    family_first_generation = _family_first_generation(registry)
    # Resolve the predecessor ONCE, and refuse with the governed code rather
    # than letting a bare OSError escape.  The strict resolve used to sit
    # inside the gate condition below, where an absent directory raised
    # FileNotFoundError straight out of generate_freeze_receipt.  That was
    # unreachable while no registry carried a generation threshold (the `and`
    # short-circuited on `family_first_generation is None`); the ruled registry
    # supplies one, so the expression is now evaluated on every call.  This is
    # an intentional fail-closed scope expansion from predecessor-only guarded
    # resolution: every supplied predecessor is now resolved before the gate
    # predicate, even when its generation would not engage publication.
    predecessor_root: Path | None = None
    if predecessor_pack_root is not None:
        try:
            predecessor_root = Path(predecessor_pack_root).resolve(strict=True)
        except OSError as exc:
            raise _successor_chain_refusal(
                f"predecessor pack root is unreadable: {exc}"
            ) from exc
        expected_predecessor = _RULED_V5_PREDECESSOR_PACK_IDS.get(root.name)
        if (
            expected_predecessor is not None
            and predecessor_root.name != expected_predecessor
        ):
            raise _successor_chain_refusal(
                "the ruled _v5 family requires its authenticated _v3 predecessor"
            )
    if (
        predecessor_root is not None
        and _pack_generation(predecessor_root.name) >= family_first_generation
    ):
        try:
            _gate_family_publication(
                predecessor_root,
                marker_path=family_publication_marker,
                confirmation_path=step6_confirmation_table,
                expected_confirmation_digest=expected_confirmation_digest,
            )
        except FamilyPublicationError as exc:
            predecessor_registry, _raw = load_registry(
                _repo_for_pack(Path(predecessor_pack_root))
            )
            entry = _family_refusal_entry(predecessor_registry)
            return {
                "status": "REFUSE",
                "arm_disposition": "NOT_APPLICABLE",
                "receipt_path": None,
                "receipt_sha256": None,
                "reason_codes": [entry["code"]],
                "detail": f"{exc.check_id}: {exc}",
                "mutated": False,
            }
    if generation > 1 and predecessor_pack_root is None:
        raise _successor_chain_refusal(
            "a successor pack requires an authenticated predecessor pack root"
        )
    if generation == 1 and predecessor_pack_root is not None:
        raise ArmReadinessError(
            "readiness_usage_invalid",
            "a first-generation pack cannot carry a freeze predecessor",
        )
    namespace = root / "arm_readiness.freeze.receipts"
    existing = scan_receipt_namespace(namespace, "freeze", allow_absent=True)
    if existing and readiness["freeze_receipt"] is not None:
        pinned = [
            item
            for item in existing
            if {
                "path": f"arm_readiness.freeze.receipts/{item['path'].name}",
                "sha256": item["sha256"],
            }
            == readiness["freeze_receipt"]
        ]
        if len(pinned) != 1:
            raise ArmReadinessError(
                "readiness_freeze_receipt_mismatch", "existing freeze receipt is not plan-pinned"
            )
        latest = pinned[0]
        # Idempotent replay is an active use of the receipt, not a namespace
        # lookup.  Re-authenticate the CURRENT successor in full before any
        # ``mutated: false`` conclusion: the plan-pinned receipt and sidecar,
        # ``pack_identity`` against the committed pack bytes, and every
        # referenced evidence digest including the identity-projection receipt.
        # For a v2 receipt this loader also authenticates the recorded
        # predecessor chain, so ancestry is never the only thing checked.
        # ``require_pass`` stays False because a recorded REFUSE must replay as
        # the REFUSE it is rather than raise.
        try:
            _load_freeze_reference(
                root,
                tree,
                registry_reference,
                registry,
                require_pass=False,
                step6_confirmation_table=step6_confirmation_table,
                expected_confirmation_digest=expected_confirmation_digest,
            )
        except EvidenceLifecycleError as exc:
            return {
                "status": "REFUSE",
                "arm_disposition": "NOT_APPLICABLE",
                "receipt_path": None,
                "receipt_sha256": None,
                "reason_codes": [exc.reason_code],
                "detail": str(exc),
                "mutated": False,
            }
        if (
            latest["receipt"]["schema_version"] == FREEZE_RECEIPT_V2_SCHEMA
            and predecessor_pack_root is not None
            and _derive_freeze_predecessor(root, Path(predecessor_pack_root))
            != dict(latest["receipt"]["predecessor"])
        ):
            raise _successor_chain_refusal(
                "replayed predecessor derivation differs from the recorded binding"
            )
        return {
            "status": latest["receipt"]["status"],
            "arm_disposition": "NOT_APPLICABLE",
            "receipt_path": str(latest["path"]),
            "receipt_sha256": latest["sha256"],
            "reason_codes": sorted(
                {item["code"] for item in latest["receipt"]["refusals"]}
            ),
            "mutated": False,
        }
    if existing:
        raise ArmReadinessError(
            "readiness_freeze_receipt_mismatch", "unreferenced freeze receipt exists"
        )
    _gate_measurement_checkout(root, registry, measurement_checkout)
    # Chain authentication precedes every write and every derived conclusion.
    predecessor: dict[str, Any] | None = None
    number = 1
    if generation > 1:
        predecessor = _derive_freeze_predecessor(root, Path(predecessor_pack_root))
        number = (
            _freeze_receipt_ordinal(
                predecessor["freeze_receipt"]["receipt_id"],
                "predecessor freeze receipt_id",
            )
            + 1
        )
        _authenticate_freeze_predecessor(
            root,
            predecessor,
            successor_receipt_id=f"freeze-{number:04d}",
            successor_profile=str(registry_reference["plan_profile"]),
        )
    _admit_bound_analysis_manifest(root, tree)
    # The pre-freeze pack must be an exact committed tree.  The writes below
    # intentionally make it dirty until the lead commits the final frozen pack.
    pre_freeze_pack_sha = committed_pack_tree_sha256(root)
    del pre_freeze_pack_sha
    pack = _pack_record(root)
    head = reviewed_main(root)["head_commit"]
    custody_pack_root = root
    evaluated_at_monotonic_ns = time.monotonic_ns()
    boot_session_id = _current_boot_session_id()
    evidence_items, evidence_receipts, evidence_refusals = _discover_evidence(
        root,
        custody_pack_root,
        pack_sha256=None,
        head_commit=None,
        boot_session_id=boot_session_id,
        now_monotonic_ns=evaluated_at_monotonic_ns,
        lifecycle_registry=(
            registry["freeze_evidence_lifecycle"]
            if registry["schema_version"] == R1_ROW_REGISTRY_SCHEMA
            else None
        ),
        step6_confirmation_table=step6_confirmation_table,
        expected_confirmation_digest=expected_confirmation_digest,
    )
    identity_item, identity_receipt, identity_reasons = _load_frozen_identity_evidence(
        root, tree
    )
    if identity_item is not None and identity_receipt is not None:
        evidence_items.append(identity_item)
        evidence_items.sort(key=lambda item: item["evidence_id"])
        evidence_receipts[identity_item["evidence_id"]] = identity_receipt
    definitions = _profile_rows(registry, registry_reference["plan_profile"], phase="freeze")
    rows, refusals = _evaluate_rows(
        definitions,
        evidence_receipts,
        clock_route="MANUAL",
        successor_acceptance=not _issued_d079(tree),
        forced_reason_codes={
            "desk.identity_pin_projection": identity_reasons
        },
        # Freeze issuance evaluates authenticated evidence without performing
        # the later ARM-consumption anchor check.
        live_clock_anchor=_PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE,
    )
    refusals = sorted(
        evidence_refusals + refusals,
        key=_refusal_sort_key,
    )
    status = "REFUSE" if refusals else "PASS"
    receipt_name = f"freeze-{number:04d}.json"
    receipt = {
        "schema_version": (
            FREEZE_RECEIPT_V2_SCHEMA if predecessor is not None else FREEZE_RECEIPT_SCHEMA
        ),
        "receipt_kind": "freeze",
        "receipt_id": receipt_name.removesuffix(".json"),
        "status": status,
        "arm_disposition": "NOT_APPLICABLE",
        "issued_at_utc": _utc_now(),
        "pack_identity": _pack_identity(root, tree),
        "row_registry": copy.deepcopy(registry_reference),
        "evidence": evidence_items,
        "rows": rows,
        "refusals": refusals,
        "assurance": copy.deepcopy(ASSURANCE),
    }
    if predecessor is not None:
        receipt["predecessor"] = copy.deepcopy(predecessor)
    else:
        receipt["supersedes"] = None
    validate_freeze_receipt(receipt)
    raw = render_json(receipt)
    digest = sha256_bytes(raw)
    _exclusive_write(namespace / receipt_name, raw)
    _exclusive_write(
        namespace / f"{receipt_name}.sha256", gnu_sidecar(digest, receipt_name)
    )
    tree["arm_attachments"]["arm_readiness"]["freeze_receipt"] = {
        "path": f"arm_readiness.freeze.receipts/{receipt_name}",
        "sha256": digest,
    }
    tree_raw = _render_plan_tree(tree)
    _atomic_replace(root / "plan_tree.json", tree_raw)
    _atomic_replace(
        root / "plan_tree.sha256",
        gnu_sidecar(sha256_bytes(tree_raw), "plan_tree.json"),
    )
    return {
        "status": status,
        "arm_disposition": "NOT_APPLICABLE",
        "receipt_path": str(namespace / receipt_name),
        "receipt_sha256": digest,
        "reason_codes": sorted({item["code"] for item in refusals}),
        "mutated": True,
    }


def generate_dry_run_receipt(
    pack_root: Path | str,
    window_custody_root: Path | str,
    rehearsal_id: str,
    synthetic_root: Path | str,
) -> dict[str, Any]:
    root = Path(pack_root).resolve(strict=True)
    custody_root = Path(window_custody_root).resolve()
    synthetic = Path(synthetic_root).resolve()
    _require_path_component(rehearsal_id, "rehearsal_id")
    if not synthetic.is_absolute():
        raise ArmReadinessError(
            "readiness_usage_invalid", "synthetic root must be absolute"
        )
    custody_pack_root = custody_root / root.name
    existing = scan_receipt_namespace(
        custody_pack_root / "arm_readiness.dry_run.receipts",
        "dry-run",
        allow_absent=True,
    )
    if any(
        item["receipt"]["synthetic_context"]["rehearsal_id"] == rehearsal_id
        for item in existing
    ):
        raise ArmReadinessError(
            "readiness_usage_invalid", "rehearsal_id was already used"
        )
    pack = _pack_record(root)
    tree, _tree_raw = _plan_tree(root)
    registry, _registry_raw, registry_reference = _registry_reference(root)
    try:
        freeze_receipt, _freeze_reference = _load_freeze_reference(
            root,
            tree,
            registry_reference,
            registry,
            require_pass=False,
        )
        freeze_refusals = copy.deepcopy(freeze_receipt["refusals"])
        if freeze_receipt["status"] != "PASS" and not freeze_refusals:
            freeze_refusals = [_receipt_refusal("readiness_dependency_refused")]
    except ArmReadinessError as exc:
        freeze_refusals = [exc.refusal()]
    checks = _run_under_lease_rehearsal(root, synthetic, rehearsal_id)
    reviewed = reviewed_main(root)
    head_binding = reviewed["head_commit"]
    checks.append(
        _dry_run_check(
            "same_head_pack_binding",
            ["reviewed-head", head_binding, "pack", pack["pack_sha256"]],
            0 if reviewed["clean"] and reviewed["exact_match"] else 1,
            head_binding,
            "",
        )
    )
    refusals = list(freeze_refusals)
    if any(check["status"] != "PASS" for check in checks):
        refusals.append(_receipt_refusal("readiness_ledger_preflight_refused"))
    if not reviewed["clean"]:
        refusals.append(_receipt_refusal("readiness_git_tree_dirty"))
    elif not reviewed["exact_match"]:
        refusals.append(_receipt_refusal("readiness_reviewed_main_mismatch"))
    status = "REFUSE" if refusals else "PASS"
    namespace = custody_pack_root / "arm_readiness.dry_run.receipts"
    number = max((item["number"] for item in existing), default=0) + 1
    receipt_name = f"dry-run-{number:04d}.json"
    receipt = {
        "schema_version": DRY_RUN_RECEIPT_SCHEMA,
        "receipt_kind": "dry_run",
        "receipt_id": receipt_name.removesuffix(".json"),
        "mode": "dry_run",
        "status": status,
        "arm_disposition": "NOT_APPLICABLE",
        "issued_at_utc": _utc_now(),
        "pack": pack,
        "synthetic_context": {
            "rehearsal_id": rehearsal_id,
            "root": str(synthetic),
            "ledger_path": str(synthetic / "calibration_observation_ledger.jsonl"),
            "backend": "synthetic_real_lease_replay.v1",
        },
        "evidence": [],
        "checks": checks,
        "omitted_live_domains": list(SYNTHETIC_DOMAINS),
        "refusals": sorted(
            refusals,
            key=_refusal_sort_key,
        ),
        "assurance": copy.deepcopy(ASSURANCE),
    }
    validate_dry_run_receipt(receipt)
    raw = render_json(receipt)
    digest = sha256_bytes(raw)
    _exclusive_write(namespace / receipt_name, raw)
    _exclusive_write(
        namespace / f"{receipt_name}.sha256", gnu_sidecar(digest, receipt_name)
    )
    return {
        "status": status,
        "arm_disposition": "NOT_APPLICABLE",
        "receipt_path": str(namespace / receipt_name),
        "receipt_sha256": digest,
        "reason_codes": sorted({item["code"] for item in receipt["refusals"]}),
    }


def generate_arm_receipt(
    pack_root: Path | str,
    arm_context: Mapping[str, Any],
    window_custody_root: Path | str,
    *,
    validity_ns: int = 300_000_000_000,
    family_publication_marker: Path | str | None = None,
    step6_confirmation_table: Path | str | None = None,
    expected_confirmation_digest: str | None = None,
) -> dict[str, Any]:
    root = Path(pack_root).resolve(strict=True)
    try:
        _gate_receipt_histsem(root)
    except HistoricalSemanticsError as exc:
        return {
            "status": "REFUSE",
            "arm_disposition": "NO_GO",
            "receipt_path": None,
            "receipt_sha256": None,
            "reason_codes": [exc.reason_code],
            "detail": str(exc),
        }
    context = validate_arm_context(arm_context)
    publication_root = Path(window_custody_root).resolve() / "family_publication"
    marker_path = (
        Path(family_publication_marker)
        if family_publication_marker is not None
        else publication_root / FAMILY_PUBLICATION_MARKER_NAME
    )
    confirmation_path = (
        Path(step6_confirmation_table)
        if step6_confirmation_table is not None
        else publication_root / STEP6_CONFIRMATION_TABLE_NAME
    )
    pack = _pack_record(root)
    reviewed = reviewed_main(root)
    tree, _tree_raw = _plan_tree(root)
    registry, _registry_raw, registry_reference = _registry_reference(root)
    try:
        freeze_receipt, freeze_reference = _load_freeze_reference(
            root,
            tree,
            registry_reference,
            registry,
            require_pass=False,
            step6_confirmation_table=confirmation_path,
            expected_confirmation_digest=expected_confirmation_digest,
        )
    except EvidenceLifecycleError as exc:
        return {
            "status": "REFUSE",
            "arm_disposition": "NO_GO",
            "receipt_path": None,
            "receipt_sha256": None,
            "reason_codes": [exc.reason_code],
            "detail": str(exc),
        }
    custody_root = Path(window_custody_root).resolve()
    custody_pack_root = custody_root / root.name
    arm_namespace = custody_pack_root / "arm_readiness.receipts"
    existing = scan_receipt_namespace(arm_namespace, "arm", allow_absent=True)
    prior_receipts = [item["receipt"] for item in existing]
    number = max((item["number"] for item in existing), default=0) + 1
    evaluated_at_monotonic_ns = time.monotonic_ns()
    boot_session_id = _current_boot_session_id()
    lifecycle_registry = (
        registry["freeze_evidence_lifecycle"]
        if registry["schema_version"] == R1_ROW_REGISTRY_SCHEMA
        else None
    )
    evidence_items, evidence_receipts, evidence_refusals = _discover_evidence(
        root,
        custody_pack_root,
        pack_sha256=pack["pack_sha256"],
        head_commit=reviewed["head_commit"],
        boot_session_id=boot_session_id,
        now_monotonic_ns=evaluated_at_monotonic_ns,
        include_pack=False,
        lifecycle_registry=lifecycle_registry,
        step6_confirmation_table=confirmation_path,
        expected_confirmation_digest=expected_confirmation_digest,
    )
    try:
        _gate_family_publication(
            root,
            marker_path=marker_path,
            confirmation_path=confirmation_path,
            expected_confirmation_digest=expected_confirmation_digest,
        )
    except FamilyPublicationError:
        entry = _family_refusal_entry(registry)
        evidence_refusals.append(
            {
                "type": entry["type"],
                "code": entry["code"],
                "row_id": None,
                "evidence_id": None,
            }
        )
    try:
        freeze_items, freeze_evidence_receipts = _freeze_evidence_for_arm(
            root,
            tree,
            freeze_receipt,
            registry,
            step6_confirmation_table=confirmation_path,
            expected_confirmation_digest=expected_confirmation_digest,
        )
    except EvidenceLifecycleError as exc:
        evidence_refusals.append(exc.refusal())
        freeze_items, freeze_evidence_receipts = [], {}
    duplicate_ids = set(evidence_receipts).intersection(freeze_evidence_receipts)
    if duplicate_ids:
        raise ArmReadinessError(
            "readiness_evidence_reference_invalid",
            f"arm and freeze evidence IDs collide: {sorted(duplicate_ids)!r}",
        )
    evidence_items.extend(freeze_items)
    evidence_items.sort(key=lambda item: item["evidence_id"])
    evidence_receipts.update(freeze_evidence_receipts)
    if lifecycle_registry is not None:
        try:
            validate_r1_temporal_budget(
                evidence_receipts.values(),
                lifecycle_registry,
                now_monotonic_ns=evaluated_at_monotonic_ns,
            )
        except EvidenceLifecycleError as exc:
            evidence_refusals.append(exc.refusal())
    identity_item, identity_receipt, identity_reasons = (
        _run_identity_arm_reverification(
            root, custody_root, str(context["bracket_session_id"])
        )
    )
    if identity_item is not None and identity_receipt is not None:
        evidence_items.append(identity_item)
        evidence_items.sort(key=lambda item: item["evidence_id"])
        evidence_receipts[identity_item["evidence_id"]] = identity_receipt
    dry_run, dry_run_item, dry_run_code = _latest_dry_run_binding(
        custody_pack_root, pack, reviewed
    )
    if dry_run is not None and dry_run_item is not None:
        evidence_items.append(dry_run_item)
        evidence_items.sort(key=lambda item: item["evidence_id"])
        evidence_receipts[dry_run_item["evidence_id"]] = (
            _dry_run_semantic_receipt(dry_run)
        )
    root_refusals, internal_passes = _root_policy_refusals(context, prior_receipts)
    root_refusals.extend(_plan_root_binding_refusals(tree, context))
    if reviewed["exact_match"]:
        internal_passes.add("desk.reviewed_checkout")
    forced: dict[str, list[str]] = {
        "desk.identity_pin_projection": list(identity_reasons)
    }
    for refusal in root_refusals:
        if refusal["row_id"] is not None:
            forced.setdefault(str(refusal["row_id"]), []).append(refusal["code"])
    definitions = _profile_rows(registry, registry_reference["plan_profile"], phase="arm")
    live_clock_anchor = _sample_live_clock_anchor()
    rows, row_refusals = _evaluate_rows(
        definitions,
        evidence_receipts,
        clock_route=context["clock_route"],
        successor_acceptance=not _issued_d079(tree),
        internal_passes=internal_passes,
        forced_reason_codes=forced,
        expected_plan_sha256=_pack_identity(root, tree)["plan_sha256"],
        # This is the sole original ARM evaluation: sample once and thread the
        # result into the source-discriminated clock predicate.
        live_clock_anchor=live_clock_anchor,
    )
    refusals = list(evidence_refusals) + list(root_refusals) + row_refusals
    if freeze_receipt["status"] != "PASS":
        refusals.append(_receipt_refusal("readiness_dependency_refused"))
    if not reviewed["clean"]:
        refusals.append(_receipt_refusal("readiness_git_tree_dirty", row_id="desk.reviewed_checkout"))
    elif not reviewed["exact_match"]:
        refusals.append(
            _receipt_refusal("readiness_reviewed_main_mismatch", row_id="desk.reviewed_checkout")
        )
    if dry_run_code is not None:
        refusals.append(_receipt_refusal(dry_run_code, row_id="desk.under_lease_rehearsal"))
    # De-duplicate exact refusal records without weakening any row refusal.
    unique = {
        (item["type"], item["code"], item["row_id"], item["evidence_id"]): item
        for item in refusals
    }
    refusals = sorted(
        unique.values(),
        key=_refusal_sort_key,
    )
    status = "REFUSE" if refusals else "PASS"
    receipt_name = f"arm-{number:04d}.json"
    supersedes = None
    if existing:
        prior = existing[-1]
        supersedes = {
            "receipt_id": prior["receipt"]["receipt_id"],
            "receipt_path": f"arm_readiness.receipts/{prior['path'].name}",
            "receipt_sha256": prior["sha256"],
            "pack_id": prior["receipt"]["pack"]["pack_id"],
            "pack_sha256": prior["receipt"]["pack"]["pack_sha256"],
        }
    evidence_expirations = [
        int(item["valid_until_monotonic_ns"])
        for item in evidence_receipts.values()
        if "valid_until_monotonic_ns" in item
    ]
    arm_horizon_ns = (
        int(lifecycle_registry["arm_policy"]["capability_horizon_ns"])
        if lifecycle_registry is not None
        else validity_ns
    )
    valid_until = min(
        [evaluated_at_monotonic_ns + arm_horizon_ns, *evidence_expirations]
    )
    receipt = {
        "schema_version": ARM_RECEIPT_SCHEMA,
        "receipt_kind": "arm",
        "receipt_id": receipt_name.removesuffix(".json"),
        "mode": "arm",
        "status": status,
        "arm_disposition": "NO_GO" if refusals else "GO",
        "issued_at_utc": _utc_now(),
        "boot_session_id": boot_session_id,
        "valid_until_monotonic_ns": valid_until,
        "pack": pack,
        "reviewed_main": reviewed,
        "arm_context": copy.deepcopy(dict(context)),
        "freeze_receipt": freeze_reference,
        "row_registry": copy.deepcopy(registry_reference),
        "evidence": evidence_items,
        "rows": rows,
        "refusals": refusals,
        "supersedes": supersedes,
        "assurance": copy.deepcopy(ASSURANCE),
    }
    validate_arm_receipt(receipt)
    raw = render_json(receipt)
    digest = sha256_bytes(raw)
    _exclusive_write(arm_namespace / receipt_name, raw)
    _exclusive_write(
        arm_namespace / f"{receipt_name}.sha256", gnu_sidecar(digest, receipt_name)
    )
    return {
        "status": status,
        "arm_disposition": receipt["arm_disposition"],
        "receipt_path": str(arm_namespace / receipt_name),
        "receipt_sha256": digest,
        "reason_codes": sorted({item["code"] for item in refusals}),
    }


def _consume_launch_capability(
    *,
    pack_root: Path | str = _MISSING_LAUNCH_CONTEXT,
    arm_receipt: Path | str = _MISSING_LAUNCH_CONTEXT,
    authenticated_arm_receipt: Mapping[str, Any] = _MISSING_LAUNCH_CONTEXT,
    arm_receipt_sha256: str = _MISSING_LAUNCH_CONTEXT,
    window_custody_root: Path | str = _MISSING_LAUNCH_CONTEXT,
    launch_manifest: Path | str = _MISSING_LAUNCH_CONTEXT,
    authenticated_launch_manifest: Mapping[str, Any] = _MISSING_LAUNCH_CONTEXT,
    launch_manifest_sha256: str = _MISSING_LAUNCH_CONTEXT,
    window_plan_root: Path | str = _MISSING_LAUNCH_CONTEXT,
    window_environment_sha256: str = _MISSING_LAUNCH_CONTEXT,
    window_chain_sha256: str = _MISSING_LAUNCH_CONTEXT,
    exec_argv: Sequence[str] = _MISSING_LAUNCH_CONTEXT,
    handoff_token_sha256: str = _MISSING_LAUNCH_CONTEXT,
    night_plan: Path | str = _MISSING_LAUNCH_CONTEXT,
    go_receipt: Path | str = _MISSING_LAUNCH_CONTEXT,
    authenticated_go_receipt: Mapping[str, Any] = _MISSING_LAUNCH_CONTEXT,
    go_receipt_sha256: str = _MISSING_LAUNCH_CONTEXT,
    step6_confirmation_table: Path | str | None = _MISSING_LAUNCH_CONTEXT,
    expected_confirmation_digest: str | None = _MISSING_LAUNCH_CONTEXT,
) -> dict[str, Any]:
    """Reauthenticate complete launch inputs, then atomically claim one GO."""

    if any(
        value is _MISSING_LAUNCH_CONTEXT
        for value in (
            pack_root,
            arm_receipt,
            authenticated_arm_receipt,
            arm_receipt_sha256,
            window_custody_root,
            launch_manifest,
            authenticated_launch_manifest,
            launch_manifest_sha256,
            window_plan_root,
            window_environment_sha256,
            window_chain_sha256,
            exec_argv,
            handoff_token_sha256,
            night_plan, go_receipt, authenticated_go_receipt, go_receipt_sha256,
        )
    ):
        raise ArmReadinessError(
            "readiness_usage_invalid",
            "complete authenticated launch context is required",
        )
    if any(value is _MISSING_LAUNCH_CONTEXT or value is None for value in (
        step6_confirmation_table, expected_confirmation_digest,
    )):
        raise FamilyPublicationError("confirmation_missing", "both confirmation inputs are required")
    _admit_pack_launch_go(
        night_plan=night_plan, go_receipt=go_receipt,
        go_receipt_sha256=go_receipt_sha256,
        authenticated_go_receipt=authenticated_go_receipt,
    )
    if not isinstance(authenticated_arm_receipt, Mapping):
        raise ArmReadinessError(
            "readiness_usage_invalid",
            "authenticated arm receipt context is required",
        )
    if not isinstance(authenticated_launch_manifest, Mapping):
        raise ArmReadinessError(
            "readiness_usage_invalid",
            "authenticated launch-manifest context is required",
        )
    for value, where in (
        (pack_root, "pack_root"),
        (arm_receipt, "arm_receipt"),
        (window_custody_root, "window_custody_root"),
        (launch_manifest, "launch_manifest"),
        (window_plan_root, "window_plan_root"),
    ):
        if not isinstance(value, (str, os.PathLike)):
            raise ArmReadinessError(
                "readiness_usage_invalid", f"{where} is required"
            )
    if isinstance(exec_argv, (str, bytes)) or not isinstance(exec_argv, Sequence):
        raise ArmReadinessError(
            "readiness_usage_invalid", "exact exec argv is required"
        )
    for value, where in (
        (arm_receipt_sha256, "arm_receipt_sha256"),
        (launch_manifest_sha256, "launch_manifest_sha256"),
        (window_environment_sha256, "window_environment_sha256"),
        (window_chain_sha256, "window_chain_sha256"),
        (handoff_token_sha256, "handoff_token_sha256"),
    ):
        _require_lower_sha256(value, where)

    launch_binding_cache: dict[Path, bytes] = {}
    verified = _verify_arm_receipt(
        pack_root,
        arm_receipt,
        require_unconsumed=False,
        launch_binding_cache=launch_binding_cache,
        step6_confirmation_table=step6_confirmation_table,
        expected_confirmation_digest=expected_confirmation_digest,
    )
    root = Path(pack_root).resolve(strict=True)
    receipt_path = Path(arm_receipt).resolve(strict=True)
    receipt, _raw, digest = _read_arm_with_sidecar(receipt_path)
    if (
        dict(authenticated_arm_receipt) != dict(receipt)
        or arm_receipt_sha256 != digest
        or dict(verified)
        != {
            "status": "PASS",
            "arm_disposition": "GO",
            "receipt_path": str(receipt_path),
            "receipt_sha256": arm_receipt_sha256,
            "pack_sha256": receipt["pack"]["pack_sha256"],
        }
    ):
        raise ArmReadinessError(
            "readiness_usage_invalid",
            "authenticated arm receipt context changed before consumption",
        )
    reviewed = reviewed_main(root)
    context = receipt["arm_context"]
    root_refusals, _passes = _root_policy_refusals(context, [])
    if root_refusals:
        raise ArmReadinessError(
            root_refusals[0]["code"], "volatile root/backup/lock predicate changed"
        )
    custody_pack_root = Path(window_custody_root).resolve() / root.name
    if custody_pack_root != receipt_path.parent.parent:
        raise ArmReadinessError(
            "readiness_receipt_namespace_anomalous",
            "consumption custody root differs from the arm receipt namespace",
        )
    consumption_name = f"{receipt['receipt_id']}.consumed.json"
    relative_arm_path = f"arm_readiness.receipts/{receipt_path.name}"
    volatile_checks = sorted(
        [
            "arm_receipt_unsuperseded",
            "campaign_lock_absent",
            "pack_digest_unchanged",
            "roots_and_backups_rechecked",
            "same_head",
        ]
    )
    manifest, manifest_ref, env_ref, chain_ref = (
        _load_launch_manifest_for_consumption(
            Path(launch_manifest),
            launch_binding_cache=launch_binding_cache,
        )
    )
    try:
        authenticated_manifest = validate_launch_manifest(
            authenticated_launch_manifest
        )
    except (OSError, RuntimeError) as exc:
        raise ArmReadinessError(
            "readiness_evidence_unreadable",
            f"assembled launch root is unavailable: {exc}",
        ) from exc
    if dict(authenticated_manifest) != dict(manifest):
        raise ArmReadinessError(
            "readiness_usage_invalid",
            "assembled launch context changed before consumption",
        )
    _reconcile_launch_binding(
        pack_root=root,
        custody_pack_root=custody_pack_root,
        window_custody_root=Path(window_custody_root),
        arm_receipt=receipt,
        manifest=manifest,
        manifest_reference=manifest_ref,
        launch_manifest_sha256=launch_manifest_sha256,
        window_plan_root=Path(window_plan_root),
        window_environment_reference=env_ref,
        window_environment_sha256=window_environment_sha256,
        window_chain_reference=chain_ref,
        window_chain_sha256=window_chain_sha256,
        exec_argv=exec_argv,
        launch_binding_cache=launch_binding_cache,
    )
    pack = receipt["pack"]
    consumed_at = time.monotonic_ns()
    go_fields, go_bounds = _authenticate_pack_launch_go(
        night_plan=night_plan, go_receipt=go_receipt,
        authenticated_go_receipt=authenticated_go_receipt,
        go_receipt_sha256=go_receipt_sha256, arm=receipt, arm_sha256=digest,
        custody_pack_root=custody_pack_root, manifest_ref=manifest_ref,
        env_ref=env_ref, chain_ref=chain_ref,
        step6_confirmation_table=step6_confirmation_table,
        expected_confirmation_digest=expected_confirmation_digest,
        require_current_boot=True, at_monotonic_ns=consumed_at,
        launch_binding_cache=launch_binding_cache,
    )
    consumption = {
        "schema_version": CONSUMPTION_RECEIPT_SCHEMA,
        "receipt_kind": "launch_consumption",
        "consumption_id": f"{receipt['receipt_id']}-launch",
        "consumed_at_utc": _utc_now(),
        "consumed_at_monotonic_ns": consumed_at,
        "boot_session_id": receipt["boot_session_id"],
        "pack_id": pack["pack_id"],
        "pack_sha256": verified["pack_sha256"],
        "plan_id": pack["plan_id"],
        "window_id": pack["window_id"],
        "arm_receipt": {
            "receipt_id": receipt["receipt_id"],
            "path": relative_arm_path,
            "sha256": digest,
        },
        "head_commit": reviewed["head_commit"],
        "arm_context_sha256": sha256_bytes(render_json(context)),
        "launch_manifest": manifest_ref,
        "window_environment": env_ref,
        "window_chain": chain_ref,
        "exec_argv": list(exec_argv),
        "handoff_token_sha256": handoff_token_sha256,
        "volatile_checks": volatile_checks,
        "assurance": copy.deepcopy(ASSURANCE),
    }
    consumption.update(go_fields)
    validate_consumption_receipt(consumption)
    raw = render_json(consumption)
    consumption_dir = custody_pack_root / "arm_readiness.consumptions"
    consumption_dir.mkdir(parents=True, exist_ok=True)
    _fsync_directory(custody_pack_root)
    consumption_path = consumption_dir / consumption_name
    # Python caller identity is not authenticated here.  This atomic
    # no-clobber primary is the only real enforcement and the single-use
    # linearization point; every later complete caller must lose this write.
    consumed_at = time.monotonic_ns()
    if not go_bounds[0] <= consumed_at < go_bounds[1]:
        raise _go_invalid("monotonic_ns")
    consumption["consumed_at_monotonic_ns"] = consumed_at
    raw = render_json(consumption)
    try:
        _exclusive_write(consumption_path, raw)
    except ArmReadinessError as exc:
        if exc.reason_code == "readiness_output_collision":
            raise ArmReadinessError(
                "readiness_record_consumed", "launch capability was already consumed"
            ) from exc
        raise
    _fsync_directory(consumption_dir)
    digest_out = sha256_bytes(raw)
    _exclusive_write(
        consumption_dir / f"{consumption_name}.sha256",
        gnu_sidecar(digest_out, consumption_name),
    )
    _fsync_directory(consumption_dir)
    return {
        "status": "CONSUMED",
        "arm_disposition": "NOT_APPLICABLE",
        "consumption_path": str(consumption_path),
        "consumption_sha256": digest_out,
    }


def record_launch_lifecycle_event(
    pack_root: Path | str,
    consumption_receipt: Path | str,
    event: str,
    *,
    handoff_token: bytes | None = None,
) -> dict[str, Any]:
    """Append one start/settle/completion receipt with no-clobber custody."""

    if event not in {"start", "settle", "completion"}:
        raise LaunchLineageError(
            "launch_consumption_invalid", f"unknown launch lifecycle event {event!r}"
        )
    consumption, _raw, consumption_digest, consumption_path = (
        _read_launch_consumption(consumption_receipt, require_current_boot=False)
    )
    arm, _arm_path, _recorded_pack_root, _pack = _replay_consumed_arm(
        Path(pack_root),
        consumption,
        consumption_path,
        require_current_boot=False,
        require_unexpired=False,
        replay_arm_semantics=False,
    )
    try:
        current_boot = _current_boot_session_id()
    except ArmReadinessError as exc:
        raise LaunchLineageError("launch_binding_mismatch", str(exc)) from exc
    if current_boot != consumption["boot_session_id"]:
        raise LaunchLineageError(
            "launch_binding_mismatch", "launch lifecycle crossed a boot boundary"
        )
    if event == "start":
        if handoff_token is None or sha256_bytes(handoff_token) != consumption[
            "handoff_token_sha256"
        ]:
            raise LaunchLineageError(
                "launch_handoff_invalid", "inherited one-use handoff token is absent or invalid"
            )
        predecessor = _reference_for_existing_receipt(
            consumption_path, consumption_digest
        )
        predecessor_monotonic_ns = consumption["consumed_at_monotonic_ns"]
        handoff_digest: str | None = consumption["handoff_token_sha256"]
        schema = LAUNCH_START_RECEIPT_SCHEMA
        kind = "launch_start"
    else:
        predecessor_event = "start" if event == "settle" else "settle"
        predecessor_kind = f"launch_{predecessor_event}"
        predecessor_path = _lifecycle_receipt_path(
            consumption_path, predecessor_event, require_current_boot=False
        )
        predecessor_receipt, predecessor_digest, predecessor_path = (
            _read_lifecycle_receipt(
                predecessor_path, expected_kind=predecessor_kind
            )
        )
        predecessor = _reference_for_existing_receipt(
            predecessor_path, predecessor_digest
        )
        predecessor_monotonic_ns = predecessor_receipt[
            "issued_at_monotonic_ns"
        ]
        handoff_digest = None
        schema = (
            LAUNCH_SETTLE_RECEIPT_SCHEMA
            if event == "settle"
            else LAUNCH_COMPLETION_RECEIPT_SCHEMA
        )
        kind = f"launch_{event}"
    issued_monotonic_ns = time.monotonic_ns()
    if issued_monotonic_ns < predecessor_monotonic_ns:
        raise LaunchLineageError(
            "launch_binding_mismatch", "launch lifecycle monotonic order reversed"
        )
    receipt = {
        "schema_version": schema,
        "receipt_kind": kind,
        "receipt_id": f"{consumption['consumption_id']}-{event}",
        "issued_at_utc": _utc_now(),
        "issued_at_monotonic_ns": issued_monotonic_ns,
        "boot_session_id": consumption["boot_session_id"],
        "pack_id": consumption["pack_id"],
        "pack_sha256": consumption["pack_sha256"],
        "plan_id": consumption["plan_id"],
        "window_id": consumption["window_id"],
        "bracket_session_id": arm["arm_context"]["bracket_session_id"],
        "window_chain": copy.deepcopy(dict(consumption["window_chain"])),
        "consumption": _reference_for_existing_receipt(
            consumption_path, consumption_digest
        ),
        "predecessor": predecessor,
        "handoff_token_sha256": handoff_digest,
        "assurance": copy.deepcopy(ASSURANCE),
    }
    validate_launch_lifecycle_receipt(receipt)
    path = _lifecycle_receipt_path(consumption_path, event, require_current_boot=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    _fsync_directory(path.parent.parent)
    raw = render_json(receipt)
    try:
        _exclusive_write(path, raw)
    except ArmReadinessError as exc:
        if event == "start" and exc.reason_code == "readiness_output_collision":
            raise LaunchLineageError(
                "launch_handoff_invalid", "launch handoff was already consumed"
            ) from exc
        raise LaunchLineageError(
            "launch_consumption_invalid", f"cannot record launch lifecycle: {exc}"
        ) from exc
    _fsync_directory(path.parent)
    digest = sha256_bytes(raw)
    try:
        _exclusive_write(
            path.with_name(f"{path.name}.sha256"),
            gnu_sidecar(digest, path.name),
        )
        _fsync_directory(path.parent)
    except ArmReadinessError as exc:
        # The primary is the durable append point. A missing sidecar remains
        # an incomplete, burned lifecycle and is never repaired in place.
        raise LaunchLineageError(
            "launch_consumption_invalid", f"lifecycle sidecar publication failed: {exc}"
        ) from exc
    launch_lineage = _launch_lineage_for_event(
        consumption,
        consumption_path,
        consumption_digest,
        arm,
        event,
        path,
        digest,
    )
    if event == "settle":
        claim_root = Path(str(arm["arm_context"]["claim_runs_root"]))
        bound_root = Path(str(arm["arm_context"]["bound_runs_root"]))
        try:
            if claim_root.resolve(strict=True) == bound_root.resolve(strict=True):
                raise LaunchLineageError(
                    "launch_binding_mismatch",
                    "claim and bound runs roots must be distinct locator namespaces",
                )
        except OSError as exc:
            raise LaunchLineageError(
                "launch_binding_mismatch",
                f"authenticated runs root is unavailable: {exc}",
            ) from exc
        # Fixed order is deliberate. Any failure after either no-clobber
        # primary leaves the settle receipt durable and makes retry impossible.
        _publish_launch_lineage_locator(
            claim_root,
            root_role="claim_runs_root",
            launch_lineage=launch_lineage,
        )
        _publish_launch_lineage_locator(
            bound_root,
            root_role="bound_runs_root",
            launch_lineage=launch_lineage,
        )
    return {
        "status": "RECORDED",
        "event": event,
        "receipt_path": str(path),
        "receipt_sha256": digest,
        "launch_lineage": launch_lineage,
    }


_issuer_functions = {name: value for name, value in list(globals().items())
                     if callable(value) and getattr(value, "__module__", None) == __name__}

def _fixture_issuer(function):
    @wraps(function)
    def invoke(*args, **kwargs):
        namespace = dict(vars(_readers))
        for name, original in _issuer_functions.items():
            namespace[name] = FunctionType(original.__code__, namespace, name,
                                           original.__defaults__, original.__closure__)
            namespace[name].__kwdefaults__ = original.__kwdefaults__
        return namespace[function.__name__](*args, **kwargs)
    return invoke

for _name, _function in _issuer_functions.items():
    globals()[_name] = _fixture_issuer(_function)
