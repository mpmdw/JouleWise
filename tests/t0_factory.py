"""Synthetic T-0 receipt publication for historical reader fixtures only.

No production module imports this factory. Every invocation resolves current
physical_checks globals so reader/probe patches in the calling fixture apply.
"""
from __future__ import annotations
from functools import wraps as _wraps
from types import FunctionType as _FunctionType
from joulewise import physical_checks as _physical

def _publish_staged_namespaces(
    staged_sources: _Path,
    staged_evidence: _Path,
    staged_marker: _Path,
    source_dir: _Path,
    evidence_dir: _Path,
) -> None:
    """Publish two directories with a last-written authenticated marker.

    APFS cannot atomically rename two sibling destinations as one transaction.
    Crash matrix: before rename 1 leaves the full pre-state; after rename 1
    leaves sources only, so required ARM rows are absent; after rename 2 leaves
    the evidence receipt without its marker/sidecar, so discovery refuses the
    namespace as unreadable; during rename 3, atomic rename leaves either that
    detectable marker-absent state or the complete state; after rename 3 the
    full governed set is visible.  Never roll back a partial publication:
    process death cannot make rollback reliable, while marker absence is an
    unambiguous recovery signal.
    """

    _os.replace(staged_sources, source_dir)
    _os.replace(staged_evidence, evidence_dir)
    _os.replace(staged_marker, evidence_dir / _PUBLICATION_COMPLETION_MARKER)



def author_arm_readiness_evidence_t0(
    pack_root: _Path | str,
    custody_root: _Path | str,
) -> dict[str, _Any]:
    """Author all fifteen evidence-backed ARM_ONLY row receipts."""

    root = _Path(pack_root).resolve(strict=True)
    repository = _readiness._repo_for_pack(root).resolve(strict=True)
    if repository != _RUNNING_REPOSITORY.resolve(strict=True):
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_t0_repository_mismatch",
            "pack repository differs from the executing T-0 evidence author",
        )
    custody = _Path(custody_root).resolve(strict=True)
    if not custody.is_dir() or custody.is_symlink():
        raise _underivable("AUTHORING_SET", "custody root is not a regular directory")
    reviewed = _readiness.reviewed_main(root)
    if not reviewed["clean"] or not reviewed["exact_match"]:
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_t0_reviewed_tree_mismatch",
            "reviewed checkout is dirty or differs from local/origin main",
        )
    head = reviewed["head_commit"]
    head_tree = reviewed["head_tree_oid"]
    if _GIT_RE.fullmatch(str(head)) is None or _GIT_RE.fullmatch(str(head_tree)) is None:
        raise _underivable("AUTHORING_SET", "reviewed HEAD/tree identity is unavailable")
    tree, _tree_raw = _readiness._plan_tree(root)
    try:
        frozen_plan = _readiness.resolve_frozen_plan(root, tree)
    except _readiness.ArmReadinessError as exc:
        raise _underivable(
            "AUTHORING_SET", f"R2 frozen-plan reference is invalid: {exc}"
        ) from exc
    try:
        pack_sha = _readiness.committed_pack_tree_sha256(root)
    except _readiness.ArmReadinessError as exc:
        raise _refuse("AUTHORING_SET", "evidence_author_t0_pack_uncommitted", str(exc)) from exc
    boot_session, boot_probe = _boot_probe(repository)
    context = _DerivationContext(
        pack_root=root,
        repository=repository,
        custody_root=custody,
        custody_pack_root=custody / root.name,
        tree=tree,
        pack_sha256=pack_sha,
        plan_sha256=_readiness.sha256_bytes(frozen_plan[3]),
        head_commit=str(head),
        head_tree_oid=str(head_tree),
        boot_session_id=boot_session,
        boot_probe=boot_probe,
    )
    context.values["frozen_plan"] = frozen_plan
    rows = _required_rows(context)
    _require_window_chain_presence(context, kind="CLOCK_ATTESTATION")
    source_dir = context.custody_pack_root / _SOURCE_DIRECTORY
    evidence_dir = context.custody_pack_root / _EVIDENCE_DIRECTORY
    if source_dir.exists() or evidence_dir.exists():
        if not _publication_complete(source_dir, evidence_dir):
            raise _refuse(
                "AUTHORING_SET",
                "evidence_author_t0_publication_incomplete",
                "T-0 publication is incomplete; recovery must preserve and inspect "
                "the marker-absent namespace",
            )
        return _authenticate_existing(context, rows)
    derived: list[_DerivedRow] = []
    for row in rows:
        row_id = str(row["row_id"])
        try:
            item = _DERIVERS[row_id](context)
        except T0EvidenceAuthoringError:
            raise
        except Exception as exc:
            raise _underivable(_ROW_KIND[row_id], f"unexpected derivation failure: {exc}") from exc
        if item.row_id != row_id or item.kind != _ROW_KIND[row_id]:
            raise _refuse(_ROW_KIND[row_id], "evidence_author_t0_internal_error", "deriver returned the wrong row/kind")
        derived.append(item)
    _validate_capture_order(context)
    issued_at = context.clock.utc_now()
    validity_origin = context.clock.monotonic_ns()
    sources: dict[str, bytes] = {}
    receipts: dict[str, bytes] = {}
    semantic: dict[str, _Mapping[str, _Any]] = {}
    definitions = {row["row_id"]: row for row in rows}
    for item in derived:
        source_raw = _source_bytes(context, item)
        sources[f"{_slug(item.row_id)}.json"] = source_raw
        receipt = _assemble_receipt(
            context,
            item,
            source_raw,
            issued_at_utc=issued_at,
            valid_until_monotonic_ns=(
                validity_origin + _validity_horizon_ns(item.kind)
            ),
        )
        if not _readiness._predicate_passes(
            receipt,
            definitions[item.row_id]["predicate_id"],
            expected_plan_sha256=context.plan_sha256,
            # Issuance proves the published numeric relations; the separate
            # live anchor check belongs only to original ARM evaluation.
            live_clock_anchor=_readiness._PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE,
        ):
            raise _refuse(item.kind, "evidence_author_t0_predicate_refused", f"derived facts do not satisfy {item.row_id}")
        raw = _readiness.render_json(receipt)
        name = _receipt_name(item.row_id)
        receipts[name] = raw
        receipts[f"{name}.sha256"] = _readiness.gnu_sidecar(_readiness.sha256_bytes(raw), name)
        semantic[receipt["evidence_id"]] = receipt
    _reauthenticate_artifacts(context, derived)
    if _readiness.reviewed_main(root) != reviewed or _readiness.committed_pack_tree_sha256(root) != pack_sha:
        raise _refuse("AUTHORING_SET", "evidence_author_t0_input_changed", "HEAD, tree, or pack changed during derivation")
    second_boot, _second_boot_probe = _boot_probe(repository)
    if second_boot != boot_session:
        raise _refuse("AUTHORING_SET", "evidence_author_t0_input_changed", "boot session changed during derivation")

    context.custody_pack_root.mkdir(parents=True, exist_ok=True)
    staging = _Path(_tempfile.mkdtemp(prefix=".arm-readiness-t0-", dir=context.custody_pack_root))
    try:
        staged_sources = staging / _SOURCE_DIRECTORY
        staged_evidence = staging / _EVIDENCE_DIRECTORY
        staged_sources.mkdir()
        staged_evidence.mkdir()
        for name, raw in sources.items():
            (staged_sources / name).write_bytes(raw)
        for name, raw in receipts.items():
            (staged_evidence / name).write_bytes(raw)
        items, discovered, refusals = _readiness._discover_evidence(
            root,
            staging,
            pack_sha256=pack_sha,
            head_commit=head,
            boot_session_id=boot_session,
            now_monotonic_ns=context.clock.monotonic_ns(),
            include_pack=False,
        )
        if refusals or set(discovered) != set(semantic):
            raise _refuse("AUTHORING_SET", "evidence_author_t0_validation_failed", f"staged discovery refused: {refusals!r}")
        for receipt in discovered.values():
            _readiness.validate_evidence_receipt(receipt)
        if source_dir.exists() or evidence_dir.exists():
            raise _refuse("AUTHORING_SET", "evidence_author_t0_output_collision", "T-0 output namespace appeared during derivation")
        marker_in_directory = staged_evidence / _PUBLICATION_COMPLETION_MARKER
        if not marker_in_directory.is_file() or marker_in_directory.is_symlink():
            raise _refuse(
                "AUTHORING_SET",
                "evidence_author_t0_internal_error",
                "staged publication completion marker is absent",
            )
        staged_marker = staging / _PUBLICATION_COMPLETION_MARKER
        _os.replace(marker_in_directory, staged_marker)
        try:
            _publish_staged_namespaces(
                staged_sources,
                staged_evidence,
                staged_marker,
                source_dir,
                evidence_dir,
            )
        except Exception as exc:
            raise _refuse(
                "AUTHORING_SET",
                "evidence_author_t0_publication_interrupted",
                "T-0 publication was interrupted; the completion marker records "
                "whether recovery sees a partial or complete namespace",
            ) from exc
        paths = [str(context.custody_pack_root / item["path"]) for item in sorted(items, key=lambda value: value["evidence_id"])]
    finally:
        _shutil.rmtree(staging, ignore_errors=True)
    return {
        "status": "PASS",
        "authored_rows": [row["row_id"] for row in rows],
        "authored_kinds": sorted(set(_ROW_KIND[row["row_id"]] for row in rows)),
        "receipt_paths": paths,
        "mutated": True,
    }



def _assert_public_author_signature() -> None:
    parameters = tuple(_inspect.signature(author_arm_readiness_evidence_t0).parameters)
    if parameters != ("pack_root", "custody_root"):
        raise AssertionError("public T-0 evidence author must accept exactly pack_root and custody_root")



_factory_functions = {
    name: value for name, value in list(globals().items())
    if isinstance(value, _FunctionType) and value.__module__ == __name__
}


def _fixture_function(function):
    @_wraps(function)
    def invoke(*args, **kwargs):
        namespace = dict(vars(_physical))
        for name, original in _factory_functions.items():
            clone = _FunctionType(original.__code__, namespace, name,
                                  original.__defaults__, original.__closure__)
            clone.__kwdefaults__ = original.__kwdefaults__
            namespace[name] = clone
        return namespace[function.__name__](*args, **kwargs)
    return invoke


for _name, _function in _factory_functions.items():
    globals()[_name] = _fixture_function(_function)
