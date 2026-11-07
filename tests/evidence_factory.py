"""Synthetic generic evidence records for historical reader fixtures only."""
from __future__ import annotations
from joulewise import evidence_replay as _replay
from types import FunctionType

def author_arm_readiness_evidence(
    pack_root: Path | str,
    *,
    step6_confirmation_table: Path | str | None = None,
    expected_confirmation_digest: str | None = None,
) -> dict[str, Any]:
    """Author every applicable generic FREEZE_AND_ARM evidence receipt.

    Boot identity, clocks, hashes, HEAD, facts, statuses, suite outcomes, and
    names have no API arguments and are always derived here.
    """

    root = Path(pack_root).resolve(strict=True)
    repository = _readiness._repo_for_pack(root)
    tree, _tree_raw = _readiness._plan_tree(root)
    rows, kinds = _required_generic_rows(root, tree)
    lifecycle_registry = _r1_lifecycle_registry_for_pack(root)
    r1_policies = (
        _r1_policies_for_kinds(lifecycle_registry, kinds)
        if lifecycle_registry is not None
        else None
    )
    unsupported = sorted(set(kinds) - set(_DERIVERS))
    if unsupported:
        raise _refuse(
            unsupported[0],
            "evidence_author_kind_unsupported",
            f"no production deriver for registry kind(s): {unsupported!r}",
        )
    source_dir = root / _SOURCE_DIRECTORY
    evidence_dir = root / _EVIDENCE_DIRECTORY
    if source_dir.exists() or evidence_dir.exists():
        if lifecycle_registry is not None and r1_policies is not None:
            return _authenticate_existing_r1(
                root,
                repository,
                tree,
                rows,
                kinds,
                lifecycle_registry,
                r1_policies,
                step6_confirmation_table=step6_confirmation_table,
                expected_confirmation_digest=expected_confirmation_digest,
            )
        return _authenticate_existing(
            root,
            repository,
            tree,
            rows,
            kinds,
        )

    try:
        pack_sha = _readiness.committed_pack_tree_sha256(root)
    except _readiness.ArmReadinessError as exc:
        raise _refuse(
            "PACK_AUTHENTICATION",
            "evidence_author_pack_uncommitted",
            str(exc),
        ) from exc
    head = _readiness.reviewed_main(root)["head_commit"]
    if not isinstance(head, str) or _GIT_RE.fullmatch(head) is None:
        raise _refuse(
            "PACK_AUTHENTICATION",
            "evidence_author_head_underivable",
            "HEAD commit is not derivable",
        )
    context = _DerivationContext(
        pack_root=root,
        repository=repository,
        tree=tree,
        pack_sha256=pack_sha,
        head_commit=head,
    )
    derived: list[_DerivedKind] = []
    for kind in kinds:
        try:
            item = _DERIVERS[kind](context)
        except EvidenceAuthoringError:
            raise
        except Exception as exc:
            raise _underivable(kind, f"unexpected derivation failure: {exc}") from exc
        if item.kind != kind:
            raise _refuse(
                kind,
                "evidence_author_internal_error",
                "deriver returned the wrong kind",
            )
        derived.append(item)

    issued_at = _readiness._utc_now()
    boot_session_id = _readiness._current_boot_session_id()
    evaluated_at_monotonic_ns = time.monotonic_ns()
    valid_until = evaluated_at_monotonic_ns + _EVIDENCE_VALIDITY_NS
    source_bytes: dict[str, bytes] = {}
    receipt_bytes: dict[str, bytes] = {}
    semantic_receipts: dict[str, Mapping[str, Any]] = {}
    for item in derived:
        policy = r1_policies[item.kind] if r1_policies is not None else None
        environment_fingerprint = (
            _execution_environment_fingerprint(context, item.kind)
            if policy is not None and policy["freshness_class"] == "EXECUTION_BOUND"
            else None
        )
        source_raw = (
            _r1_fact_source(
                context,
                item,
                policy,
                environment_fingerprint,
            )
            if policy is not None
            else _fact_source(context, item)
        )
        source_bytes[f"{_slug(item.kind)}.json"] = source_raw
        receipt = (
            _assemble_r1_receipt(
                context,
                item,
                source_raw,
                policy,
                issued_at_utc=issued_at,
                boot_session_id=boot_session_id,
                now_monotonic_ns=evaluated_at_monotonic_ns,
                environment_fingerprint=environment_fingerprint,
            )
            if policy is not None
            else _assemble_receipt(
                context,
                item,
                source_raw,
                issued_at_utc=issued_at,
                boot_session_id=boot_session_id,
                valid_until_monotonic_ns=valid_until,
            )
        )
        raw = _readiness.render_json(receipt)
        name = _receipt_name(item.kind)
        receipt_bytes[name] = raw
        receipt_bytes[f"{name}.sha256"] = _readiness.gnu_sidecar(
            _readiness.sha256_bytes(raw), name
        )
        semantic_receipts[receipt["evidence_id"]] = receipt
    for row in rows:
        if any(kind in kinds for kind in row["required_evidence_kinds"]):
            matching = [
                receipt
                for receipt in semantic_receipts.values()
                if receipt["kind"] in row["required_evidence_kinds"]
            ]
            if not any(
                _readiness._predicate_passes(
                    item,
                    row["predicate_id"],
                    live_clock_anchor=(
                        _readiness._PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE
                    ),
                )
                for item in matching
            ):
                raise _refuse(
                    str(row["required_evidence_kinds"][0]),
                    "evidence_author_predicate_refused",
                    f"authored facts do not satisfy {row['predicate_id']}",
                )
    _reauthenticate_primary_artifacts(context, derived)
    if _readiness.reviewed_main(root)["head_commit"] != head:
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_input_changed",
            "HEAD changed during derivation",
        )
    if _readiness.committed_pack_tree_sha256(root) != pack_sha:
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_input_changed",
            "pack bytes changed during derivation",
        )

    staging = Path(tempfile.mkdtemp(prefix=".arm-readiness-evidence-", dir=root.parent))
    installed = False
    try:
        staged_sources = staging / _SOURCE_DIRECTORY
        staged_evidence = staging / _EVIDENCE_DIRECTORY
        staged_sources.mkdir()
        staged_evidence.mkdir()
        for name, raw in source_bytes.items():
            (staged_sources / name).write_bytes(raw)
        for name, raw in receipt_bytes.items():
            (staged_evidence / name).write_bytes(raw)
        if (
            _readiness.reviewed_main(root)["head_commit"] != head
            or _readiness.committed_pack_tree_sha256(root) != pack_sha
        ):
            raise _refuse(
                "AUTHORING_SET",
                "evidence_author_input_changed",
                "HEAD or pack bytes changed before publication",
            )
        if source_dir.exists() or evidence_dir.exists():
            raise _refuse(
                "AUTHORING_SET",
                "evidence_author_output_collision",
                "evidence namespace appeared during derivation",
            )
        os.replace(staged_sources, source_dir)
        try:
            os.replace(staged_evidence, evidence_dir)
        except Exception:
            shutil.rmtree(source_dir)
            raise
        installed = True
        items, discovered, refusals = _readiness._discover_evidence(
            root,
            root,
            pack_sha256=None,
            head_commit=head,
            boot_session_id=boot_session_id,
            now_monotonic_ns=time.monotonic_ns(),
            lifecycle_registry=lifecycle_registry,
        )
        if refusals or set(discovered) != set(semantic_receipts):
            raise _refuse(
                "AUTHORING_SET",
                "evidence_author_validation_failed",
                f"authored discovery refused: {refusals!r}",
            )
        for receipt in discovered.values():
            _readiness.validate_evidence_receipt(receipt)
        paths = [
            str(root / item["path"])
            for item in sorted(items, key=lambda value: value["evidence_id"])
        ]
    except Exception:
        if installed:
            shutil.rmtree(evidence_dir, ignore_errors=True)
            shutil.rmtree(source_dir, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    return {
        "status": "PASS",
        "authored_kinds": list(kinds),
        "receipt_paths": paths,
        "mutated": True,
    }

_original = author_arm_readiness_evidence
def author_arm_readiness_evidence(*args, **kwargs):
    function = FunctionType(_original.__code__, dict(vars(_replay)), _original.__name__,
                            _original.__defaults__, _original.__closure__)
    function.__kwdefaults__ = _original.__kwdefaults__
    return function(*args, **kwargs)
