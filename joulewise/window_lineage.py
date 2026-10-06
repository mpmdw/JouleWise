"""Launch lineage for HAZARD_PACK windows (block 5).

What a lineage is for
---------------------
Every ``_v5`` science config carries the run-metadata tag
``launch_lineage_required``. Before the measurement code writes or reads a
bundle from such a config, it asks ``joulewise.arm_readiness`` to
authenticate a *launch lineage*: a small record, published into the window's
two runs roots, that names the pack, plan, window and calibration bracket
session the bundle belongs to.  On the retired ``TRANSACTION_PACK`` route that
record is a chain of ARM, GO, consumption and lifecycle receipts.  On the
``HAZARD_PACK`` route the arm decision is made by the hazard modules alone, so
there are no ARM receipts.  This module is the lineage for that route.

The driver (``run_night``'s HAZARD_PACK branch) calls
:func:`publish_window_lineage` after the arm decision and before the chain
starts.  ``arm_readiness`` dispatches on schema only: a value or locator whose
``schema_version`` is :data:`HAZARD_LINEAGE_SCHEMA` or
:data:`HAZARD_LOCATOR_SCHEMA` is handed to this module, and everything else
stays on the unchanged ARM path.  Nothing here imports or calls the ARM
replay (``_replay_consumed_arm``).

What refuses and what does not
------------------------------
Doctrine (Ed, 2026-10-05): physics refuses; everything else is a flag.  The
authenticators here refuse only on:

* **Config bytes not in the pack inventory** (collection time).  The
  inventory is ``plan_tree.json``'s
  ``arm_attachments.identity_pin_projection.identity_units[].config_inventory``
  ({path, sha256} rows).  A config whose bytes are not listed would mean a
  member other than the registered one was measured.
* **The plan tree changed after publication** (collection time), because the
  inventory is read from it.  The lineage records the plan tree's SHA-256.
* **A different boot** than the one the lineage was published in (collection
  time).  Member spans are joined to the hazard monitor's journals by
  ``time.monotonic_ns()``, which restarts at boot, so a member collected after
  a reboot cannot be joined.  An unreadable boot id does not refuse: if it
  cannot be read at collection the comparison is skipped, and if it could not
  be read at publication the lineage records ``null`` and the comparison is
  skipped for the whole window (a records finding).
* **Collection after the chain exited**, i.e. ``chain.exited`` or
  ``result.json`` already exists in the driver's night directory.  After the
  chain exits, the driver's G10 tail may switch network time ON and step the
  clock, so no member may start then.
* **Completion required but absent** (analysis readers that ask for a
  finished window): ``chain.exited`` must exist.  It is the driver's record
  that the chain's processes are gone, i.e. collection physically ended.
  ``result.json`` is written only after the G10 tail and is not required; its
  absence is a records finding.  When a window's custody root has moved
  (archived, offloaded, read on another machine), readers name its new place
  with :func:`relocated_custody`.
* **A lineage too malformed to name its pack**, because then the config check
  above cannot run.

Everything else about the records (sidecars, canonical bytes, root paths,
sibling-locator agreement, the record chain, a pack digest, boot id or arm
decision that could not be recorded at publication) is reported by
:func:`audit_window_lineage` as findings for the harvest to write as
``RECORDS`` flags.  None of it stops collection.

Publication (:func:`publish_window_lineage`) refuses only when the pack's
config inventory is unusable (every tagged member would then be refused) or
the roots cannot be written.

The three window records
------------------------
``scripts/run_campaign.py`` (a protected file) applies a block limit by
following ``authentication.consumption_path`` -> ``go_receipt`` ->
``authorization`` and reading ``purpose`` and ``permitted_blocks``.  The
publisher therefore writes three small records under
``<custody_root>/window_lineage/``: ``launch.json`` -> ``go.json`` ->
``authorization.json``.  The authorization's purpose is ``HAZARD_PACK``, so
``run_campaign`` applies no block limit; its ``permitted_blocks`` value is
present only because that reader requires an integer of at least 1.
"""

from __future__ import annotations

import contextlib
import contextvars
import copy
import hashlib
import json
import os
import subprocess
import uuid
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any, Callable, Iterator, Mapping, Sequence

HAZARD_LINEAGE_SCHEMA = "joulewise.hazard_window_lineage.v1"
HAZARD_LOCATOR_SCHEMA = "joulewise.hazard_window_lineage_locator.v1"
LAUNCH_RECORD_SCHEMA = "joulewise.hazard_window_launch.v1"
GO_RECORD_SCHEMA = "joulewise.hazard_window_go.v1"
AUTHORIZATION_SCHEMA = "joulewise.hazard_window_authorization.v1"

# The consumers derive the locator path from this basename (controller.py
# selects its pre-slot route by the file's presence), so it is shared with
# the ARM locator.  The two are told apart by schema_version.
LOCATOR_BASENAME = ".joulewise-launch-lineage.json"
ROOT_ROLES = ("claim_runs_root", "bound_runs_root")
HAZARD_PURPOSE = "HAZARD_PACK"
RECORDS_DIRNAME = "window_lineage"
LAUNCH_RECORD_NAME = "launch.json"
GO_RECORD_NAME = "go.json"
AUTHORIZATION_RECORD_NAME = "authorization.json"
CHAIN_EXITED_NAME = "chain.exited"
RESULT_NAME = "result.json"

LINEAGE_KEYS = frozenset(
    {
        "schema_version",
        "collection_boot_session_id",
        "pack_id",
        "pack_sha256",
        "plan_id",
        "window_id",
        "bracket_session_id",
        "pack_root",
        "plan_tree_sha256",
        "window_context",
        "launch_record",
    }
)
WINDOW_CONTEXT_KEYS = frozenset(
    {
        "pre_attempt_id",
        "post_attempt_id",
        "claim_runs_root",
        "bound_runs_root",
        "custody_root",
        "night_dir",
    }
)
_WINDOW_CONTEXT_PATH_KEYS = (
    "claim_runs_root",
    "bound_runs_root",
    "custody_root",
    "night_dir",
)
LOCATOR_KEYS = frozenset({"schema_version", "root_role", "root_path", "launch_lineage"})
REFERENCE_KEYS = frozenset({"path", "sha256"})

# A subset of arm_readiness.LAUNCH_LINEAGE_REASON_CODES, so the dispatch can
# re-raise every refusal as the LaunchLineageError the consumers catch.
REASON_CODES = frozenset(
    {
        "launch_consumption_missing",
        "launch_consumption_invalid",
        "launch_binding_mismatch",
        "launch_lifecycle_incomplete",
    }
)

# Finding codes written by audit_window_lineage.  The harvest turns them into
# flags; the sealed flag catalog decides their effect (all are expected to be
# DISCLOSE except lineage.plan_tree_digest_differs, a pack-identity fact).
FINDING_CODES = frozenset(
    {
        "lineage.locator_unreadable",
        "lineage.locator_sidecar_mismatch",
        "lineage.locator_noncanonical",
        "lineage.locator_root_path_differs",
        "lineage.locator_role_differs",
        "lineage.sibling_lineage_differs",
        "lineage.context_root_differs",
        "lineage.record_chain_unverified",
        "lineage.arm_decision_digest_differs",
        "lineage.plan_tree_digest_differs",
        "lineage.completion_records_absent",
        "lineage.bundle_stamp_absent",
        "lineage.bundle_stamp_differs",
        "lineage.bundle_locator_digest_differs",
        # Values publication could not read; the lineage records null for the
        # first two and go.json records no arm decision for the third.
        "lineage.pack_digest_unrecorded",
        "lineage.collection_boot_unrecorded",
        "lineage.arm_decision_unrecorded",
    }
)

# Publication fields that may be recorded as unavailable instead of refusing.
UNRECORDABLE_FIELDS = frozenset({"pack_sha256", "collection_boot_session_id", "arm_decision"})

_SHA256_HEX = frozenset("0123456789abcdef")


class HazardLineageError(ValueError):
    """A refusal by the hazard-path lineage, with a registered reason code."""

    def __init__(self, reason_code: str, message: str) -> None:
        if reason_code not in REASON_CODES:
            raise ValueError(f"unregistered hazard-lineage reason code {reason_code!r}")
        super().__init__(message)
        self.reason_code = reason_code


class LineagePublicationError(RuntimeError):
    """The driver could not publish the window lineage (before the chain)."""


# ---------------------------------------------------------------------------
# Bytes


def render_json(value: Any) -> bytes:
    """Canonical bytes, identical to ``arm_readiness.render_json``."""

    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def gnu_sidecar(digest: str, filename: str) -> bytes:
    return f"{digest}  {filename}\n".encode("ascii")


def _no_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_constant(name: str) -> Any:
    raise ValueError(f"non-finite JSON constant {name}")


def _parse_object(raw: bytes) -> dict[str, Any]:
    value = json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=_no_duplicate_pairs,
        parse_constant=_reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("JSON value is not an object")
    return value


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= _SHA256_HEX


# The run-metadata tag of every marker-bearing (``_v5`` science) config; the
# same predicate as ``arm_readiness.launch_lineage_required``, which the bundle
# writer asks before stamping a lineage (not imported: arm_readiness dispatches
# into this module).
LINEAGE_REQUIRED_TAG = "launch_lineage_required"


def _bundle_config_untagged(bundle: Path) -> bool:
    """True only when the bundle's config.json reads and carries no lineage marker.

    An unreadable or malformed config proves nothing, so it is not "untagged":
    the audit then still reports a missing stamp.
    """

    try:
        config = _parse_object((Path(bundle) / "config.json").read_bytes())
    except (OSError, ValueError, RecursionError, UnicodeDecodeError):
        return False
    metadata = config.get("run_metadata")
    tags = metadata.get("tags") if isinstance(metadata, Mapping) else None
    return not (isinstance(tags, list) and LINEAGE_REQUIRED_TAG in tags)


def _is_canonical_uuid(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return str(uuid.UUID(value)) == value
    except (ValueError, AttributeError):
        return False


def _is_path_component(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and PurePosixPath(value).name == value
        and value not in {".", ".."}
        and "\\" not in value
    )


def _is_relative_member_path(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    pure = PurePosixPath(value)
    return not (
        pure.is_absolute()
        or value != pure.as_posix()
        or ".." in pure.parts
        or "." in pure.parts
    )


def _reference(path: Path, raw: bytes) -> dict[str, str]:
    return {"path": str(path), "sha256": sha256_bytes(raw)}


# ---------------------------------------------------------------------------
# Boot identity


def current_boot_session_id() -> str | None:
    """Return Darwin's ``kern.bootsessionuuid``, or None when it cannot be read.

    Read-only: ``sysctl -n`` with no assignment.
    """

    try:
        completed = subprocess.run(
            ("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid"),
            check=False,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    try:
        value = completed.stdout.decode("ascii").strip().lower()
    except UnicodeDecodeError:
        return None
    return value if _is_canonical_uuid(value) else None


# ---------------------------------------------------------------------------
# Structure


def is_hazard_lineage(value: object) -> bool:
    """True when ``value`` claims the hazard lineage schema (dispatch test)."""

    return isinstance(value, Mapping) and value.get("schema_version") == HAZARD_LINEAGE_SCHEMA


def is_hazard_locator(path: Path | str) -> bool:
    """True when the file at ``path`` claims the hazard locator schema.

    Never raises: anything unreadable or unparseable is "not hazard", so the
    caller's ARM path keeps handling it exactly as before.
    """

    try:
        value = json.loads(Path(path).read_bytes())
    except (OSError, ValueError, RecursionError):
        return False
    return isinstance(value, dict) and value.get("schema_version") == HAZARD_LOCATOR_SCHEMA


def is_hazard_runs_root(runs_root: Path | str) -> bool:
    try:
        return is_hazard_locator(Path(runs_root) / LOCATOR_BASENAME)
    except (TypeError, ValueError):
        return False


def _invalid(message: str) -> HazardLineageError:
    return HazardLineageError("launch_consumption_invalid", message)


def validate_lineage(value: object) -> Mapping[str, Any]:
    """Check the lineage's structure; refuse only what makes it unusable."""

    if not isinstance(value, Mapping):
        raise HazardLineageError("launch_consumption_missing", "hazard lineage is absent")
    if value.get("schema_version") != HAZARD_LINEAGE_SCHEMA:
        raise _invalid("hazard lineage schema_version is not " + HAZARD_LINEAGE_SCHEMA)
    if set(value) != LINEAGE_KEYS:
        raise _invalid(
            "hazard lineage keys differ: missing "
            f"{sorted(LINEAGE_KEYS - set(value))}, unknown {sorted(set(value) - LINEAGE_KEYS)}"
        )
    for name in ("pack_id", "plan_id", "window_id"):
        if not isinstance(value[name], str) or not value[name]:
            raise _invalid(f"hazard lineage {name} must be a nonempty string")
    if not _is_path_component(value["bracket_session_id"]):
        raise _invalid("hazard lineage bracket_session_id must be one path-safe component")
    # null: publication could not read the boot id or the committed pack
    # digest.  That is a records finding (audit_window_lineage), not a refusal.
    boot = value["collection_boot_session_id"]
    if boot is not None and not _is_canonical_uuid(boot):
        raise _invalid("hazard lineage collection_boot_session_id must be a canonical UUID or null")
    if value["pack_sha256"] is not None and not _is_sha256(value["pack_sha256"]):
        raise _invalid("hazard lineage pack_sha256 must be 64 lowercase hex characters or null")
    if not _is_sha256(value["plan_tree_sha256"]):
        raise _invalid("hazard lineage plan_tree_sha256 must be 64 lowercase hex characters")
    if not isinstance(value["pack_root"], str) or not Path(value["pack_root"]).is_absolute():
        raise _invalid("hazard lineage pack_root must be an absolute path")
    context = value["window_context"]
    if not isinstance(context, Mapping) or set(context) != WINDOW_CONTEXT_KEYS:
        raise _invalid("hazard lineage window_context keys are invalid")
    for name in ("pre_attempt_id", "post_attempt_id"):
        if not _is_path_component(context[name]):
            raise _invalid(f"hazard lineage window_context.{name} must be one path-safe component")
    for name in _WINDOW_CONTEXT_PATH_KEYS:
        if not isinstance(context[name], str) or not Path(context[name]).is_absolute():
            raise _invalid(f"hazard lineage window_context.{name} must be an absolute path")
    if context["claim_runs_root"] == context["bound_runs_root"]:
        raise _invalid("hazard lineage claim and bound runs roots must differ")
    record = value["launch_record"]
    if (
        not isinstance(record, Mapping)
        or set(record) != REFERENCE_KEYS
        or not isinstance(record["path"], str)
        or not Path(record["path"]).is_absolute()
        or not _is_sha256(record["sha256"])
    ):
        raise _invalid("hazard lineage launch_record must be an absolute {path, sha256} reference")
    return value


def _validate_locator(value: Mapping[str, Any]) -> Mapping[str, Any]:
    if value.get("schema_version") != HAZARD_LOCATOR_SCHEMA or set(value) != LOCATOR_KEYS:
        raise _invalid("hazard locator schema/keys are invalid")
    if value["root_role"] not in ROOT_ROLES:
        raise _invalid("hazard locator root_role is invalid")
    if not isinstance(value["root_path"], str) or not Path(value["root_path"]).is_absolute():
        raise _invalid("hazard locator root_path must be an absolute path")
    validate_lineage(value["launch_lineage"])
    return value


# ---------------------------------------------------------------------------
# Pack inventory (the kept per-member check)


def config_inventory(pack_root: Path | str, plan_tree_sha256: str) -> dict[str, str]:
    """Return {pack-relative path: sha256} from the plan tree the lineage pins.

    Refuses when the plan tree's bytes differ from ``plan_tree_sha256`` or the
    inventory rows are unusable, because then no config can be checked.
    """

    root = Path(pack_root)
    try:
        raw = (root / "plan_tree.json").read_bytes()
    except OSError as exc:
        raise HazardLineageError(
            "launch_binding_mismatch", f"pack plan tree is unreadable: {exc}"
        ) from exc
    if sha256_bytes(raw) != plan_tree_sha256:
        raise HazardLineageError(
            "launch_binding_mismatch",
            "pack plan_tree.json bytes differ from the lineage's plan_tree_sha256",
        )
    try:
        tree = _parse_object(raw)
        units = tree["arm_attachments"]["identity_pin_projection"]["identity_units"]
    except (ValueError, KeyError, TypeError) as exc:
        raise HazardLineageError(
            "launch_binding_mismatch", f"pack plan tree omits its config inventory: {exc}"
        ) from exc
    if not isinstance(units, list) or not units:
        raise HazardLineageError(
            "launch_binding_mismatch", "pack config inventory is empty or invalid"
        )
    inventory: dict[str, str] = {}
    for unit in units:
        rows = unit.get("config_inventory") if isinstance(unit, Mapping) else None
        if not isinstance(rows, list) or not rows:
            raise HazardLineageError(
                "launch_binding_mismatch", "pack config inventory unit is invalid"
            )
        for row in rows:
            if (
                not isinstance(row, Mapping)
                or set(row) != REFERENCE_KEYS
                or not _is_relative_member_path(row["path"])
                or not _is_sha256(row["sha256"])
            ):
                raise HazardLineageError(
                    "launch_binding_mismatch", "pack config inventory row is invalid"
                )
            prior = inventory.get(row["path"])
            if prior is not None and prior != row["sha256"]:
                raise HazardLineageError(
                    "launch_binding_mismatch",
                    f"pack config inventory lists {row['path']} with two digests",
                )
            inventory[row["path"]] = row["sha256"]
    return inventory


def _check_config_members(
    pack_root: Path, inventory: Mapping[str, str], config_paths: Sequence[Path | str]
) -> None:
    for config_path in config_paths:
        candidate = Path(config_path)
        try:
            if candidate.is_symlink():
                raise OSError("symlink refused")
            resolved = candidate.resolve(strict=True)
            relative = resolved.relative_to(pack_root).as_posix()
            raw = resolved.read_bytes()
        except (OSError, ValueError) as exc:
            raise HazardLineageError(
                "launch_binding_mismatch",
                f"config is outside the window's pack: {candidate}: {exc}",
            ) from exc
        if inventory.get(relative) != sha256_bytes(raw):
            raise HazardLineageError(
                "launch_binding_mismatch",
                f"config bytes are not in the pack's committed inventory: {relative}",
            )


# ---------------------------------------------------------------------------
# Authentication (called through arm_readiness's schema dispatch)


_CUSTODY_RELOCATIONS: contextvars.ContextVar[Mapping[str, Path]] = contextvars.ContextVar(
    "joulewise_hazard_custody_relocations", default=MappingProxyType({})
)


@contextlib.contextmanager
def relocated_custody(relocations: Mapping[Path | str, Path | str]) -> Iterator[None]:
    """Read windows whose custody root has moved since publication.

    A lineage records absolute paths under its window's custody root: the
    driver's night directory (``chain.exited``, ``result.json``) and the
    launch -> go -> authorization records.  After the custody root is
    archived, offloaded or copied to another machine those paths no longer
    exist.  Inside this context, a recorded path under a recorded custody
    root named in ``relocations`` ({recorded custody_root: where it is now})
    is read from the same relative place under the new root.  Every other
    path is read as recorded.  The lineage bytes themselves never change.
    """

    merged = dict(_CUSTODY_RELOCATIONS.get())
    for recorded, actual in relocations.items():
        recorded_path, actual_path = Path(recorded), Path(actual)
        if not recorded_path.is_absolute() or not actual_path.is_absolute():
            raise ValueError("custody relocations map absolute paths to absolute paths")
        merged[recorded_path.as_posix()] = actual_path
    token = _CUSTODY_RELOCATIONS.set(MappingProxyType(merged))
    try:
        yield
    finally:
        _CUSTODY_RELOCATIONS.reset(token)


def _custody_path(recorded: str, custody_root: str) -> Path:
    """Where a path the lineage recorded under ``custody_root`` lives now."""

    path = Path(recorded)
    actual_root = _CUSTODY_RELOCATIONS.get().get(Path(custody_root).as_posix())
    if actual_root is None:
        return path
    try:
        return actual_root / path.relative_to(custody_root)
    except ValueError:
        return path


def _completion_records(night_dir: Path) -> dict[str, dict[str, str] | None]:
    """The driver's completion records; only ``chain.exited`` is required.

    ``chain.exited`` is written once the chain's processes are gone, so it is
    the physical end of collection.  ``result.json`` follows only after the
    G10 tail; it is referenced when present and its absence is a records
    finding (``lineage.completion_records_absent``), not a refusal.
    """

    exited = night_dir / CHAIN_EXITED_NAME
    try:
        exited_raw = exited.read_bytes()
    except OSError as exc:
        raise HazardLineageError(
            "launch_lifecycle_incomplete",
            f"driver {CHAIN_EXITED_NAME} record is absent or unreadable: {exited}: {exc} "
            "(if the window's custody root has moved, read it inside "
            "window_lineage.relocated_custody)",
        ) from exc
    result_path = night_dir / RESULT_NAME
    try:
        result: dict[str, str] | None = _reference(result_path, result_path.read_bytes())
    except OSError:
        result = None
    return {"chain_exited": _reference(exited, exited_raw), "result": result}


def authenticate_lineage(
    value: object,
    *,
    require_completion: bool,
    expected_pack_root: Path | str | None = None,
    require_current_boot: bool = False,
    require_completion_absent: bool = False,
    boot_reader: Callable[[], str | None] | None = None,
) -> dict[str, Any]:
    """Authenticate a hazard lineage; same keyword contract as the ARM path.

    The returned context carries the keys consumers read from
    ``arm_readiness.authenticate_launch_lineage``: ``launch_lineage``,
    ``pack_root``, ``pack_sha256``, ``bracket_session_id`` and
    ``arm_context`` (with the bracket session, both attempt ids and both
    runs roots).  ``consumption_path``/``consumption_sha256`` name the
    window's launch record for run_campaign's block-limit reader.
    """

    if require_completion and require_completion_absent:
        raise ValueError("completion cannot be simultaneously required and required absent")
    lineage = validate_lineage(value)
    context = lineage["window_context"]
    if expected_pack_root is not None:
        if Path(expected_pack_root).resolve() != Path(lineage["pack_root"]).resolve():
            raise HazardLineageError(
                "launch_binding_mismatch",
                "hazard lineage names a different pack root than the caller authenticated",
            )
    recorded_boot = lineage["collection_boot_session_id"]
    if require_current_boot and recorded_boot is not None:
        current = (boot_reader or current_boot_session_id)()
        if current is not None and current != recorded_boot:
            raise HazardLineageError(
                "launch_binding_mismatch",
                "collection boot differs from the window's boot; monotonic clocks "
                "do not join across a reboot",
            )
    night_dir = _custody_path(context["night_dir"], context["custody_root"])
    if require_completion_absent:
        for name in (CHAIN_EXITED_NAME, RESULT_NAME):
            path = night_dir / name
            if path.exists() or path.is_symlink():
                raise HazardLineageError(
                    "launch_binding_mismatch",
                    f"window chain already ended ({path} exists); no new collection",
                )
    completion = _completion_records(night_dir) if require_completion else None
    record = lineage["launch_record"]
    return {
        "schema_version": HAZARD_LINEAGE_SCHEMA,
        "boot_session_id": lineage["collection_boot_session_id"],
        "pack_id": lineage["pack_id"],
        "pack_sha256": lineage["pack_sha256"],
        "plan_id": lineage["plan_id"],
        "window_id": lineage["window_id"],
        "bracket_session_id": lineage["bracket_session_id"],
        "pack_root": lineage["pack_root"],
        "plan_tree_sha256": lineage["plan_tree_sha256"],
        "arm_context": {
            "bracket_session_id": lineage["bracket_session_id"],
            **{name: context[name] for name in sorted(WINDOW_CONTEXT_KEYS)},
        },
        "launch_lineage": copy.deepcopy(dict(lineage)),
        "launch_record": dict(record),
        # Key names fixed by run_campaign._authenticated_campaign_block_limit.
        "consumption_path": record["path"],
        "consumption_sha256": record["sha256"],
        "completion": completion,
        "completion_sha256": completion["chain_exited"]["sha256"] if completion else None,
    }


def read_locator(
    path: Path | str,
    *,
    expected_root: Path | str | None = None,
    expected_role: str | None = None,
) -> tuple[Mapping[str, Any], str]:
    """Read one locator; return (locator, sha256 of its exact bytes).

    ``expected_root`` and ``expected_role`` are accepted for signature parity
    with the ARM reader.  A locator whose recorded root or role differs is a
    records finding (see :func:`audit_window_lineage`), not a refusal.
    """

    del expected_root, expected_role
    locator_path = Path(path)
    if locator_path.name != LOCATOR_BASENAME:
        raise HazardLineageError(
            "launch_binding_mismatch", "locator path does not use the fixed basename"
        )
    try:
        raw = locator_path.read_bytes()
    except OSError as exc:
        raise HazardLineageError(
            "launch_consumption_missing", f"hazard locator is absent: {locator_path}: {exc}"
        ) from exc
    try:
        value = _parse_object(raw)
    except (ValueError, RecursionError) as exc:
        raise _invalid(f"hazard locator is not one JSON object: {locator_path}: {exc}") from exc
    return _validate_locator(value), sha256_bytes(raw)


def authenticate_campaign(
    runs_root: Path | str,
    *,
    config_paths: Sequence[Path | str] = (),
    boot_reader: Callable[[], str | None] | None = None,
) -> dict[str, Any]:
    """Collection-time authentication of a runs root and its member configs.

    Same return shape as ``arm_readiness.authenticate_campaign_launch_lineage``.
    """

    try:
        selected_root = Path(runs_root).resolve(strict=True)
    except OSError as exc:
        raise HazardLineageError(
            "launch_binding_mismatch", f"runs root is unavailable: {exc}"
        ) from exc
    if not selected_root.is_dir():
        raise HazardLineageError("launch_binding_mismatch", "runs root is not a directory")
    locator, locator_digest = read_locator(
        selected_root / LOCATOR_BASENAME, expected_root=selected_root
    )
    lineage = locator["launch_lineage"]
    authenticated = authenticate_lineage(
        lineage,
        require_completion=False,
        require_current_boot=True,
        require_completion_absent=True,
        boot_reader=boot_reader,
    )
    try:
        pack_root = Path(lineage["pack_root"]).resolve(strict=True)
    except OSError as exc:
        raise HazardLineageError(
            "launch_binding_mismatch", f"window pack root is unavailable: {exc}"
        ) from exc
    inventory = config_inventory(pack_root, lineage["plan_tree_sha256"])
    _check_config_members(pack_root, inventory, config_paths)
    return {
        "launch_lineage": copy.deepcopy(dict(lineage)),
        "pack_root": str(pack_root),
        "root_role": locator["root_role"],
        "root_path": str(selected_root),
        "locator_sha256": locator_digest,
        "config_inventory": inventory,
        "authentication": {
            key: copy.deepcopy(value)
            for key, value in authenticated.items()
            if key not in {"arm_context", "launch_lineage"}
        },
    }


def authenticate_bundle(
    bundle_path: Path | str,
    *,
    lineage: Mapping[str, Any],
    locator_sha256: object = None,
    require_completion: bool,
) -> dict[str, Any]:
    """Authenticate a bundle's stamped hazard lineage (analysis readers).

    Nothing here depends on where the bundle, the runs root or the analysing
    checkout now live, so an archive copy or another checkout reads the same
    result.  With ``require_completion`` the driver's ``chain.exited`` is
    read from the recorded custody root, or from where
    :func:`relocated_custody` says it now lives.  Whether the stamp matches
    its root's locator is a records finding (:func:`audit_window_lineage`).
    """

    del bundle_path, locator_sha256
    return authenticate_lineage(lineage, require_completion=require_completion)


# ---------------------------------------------------------------------------
# Publication (driver, before the chain starts)


def _write_once(path: Path, raw: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        _fsync_directory(path.parent)


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def committed_pack_sha256(pack_root: Path | str) -> str:
    """The D-134 committed pack-tree digest (``arm_readiness``'s function).

    It raises on any untracked entry under the pack (``.DS_Store``, an editor
    swap file, ``__pycache__``) and on any git failure.  Publication then
    records ``pack_sha256: null``; the pack's identity is decided by the L4/L5
    pack-identity collector, which recomputes it from preserved bytes.
    """

    from joulewise.arm_readiness import committed_pack_tree_sha256  # noqa: PLC0415

    return committed_pack_tree_sha256(Path(pack_root))


def _describe(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"


def _canonical_boot(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        return str(uuid.UUID(value.strip()))
    except ValueError:
        return None


def publish_window_lineage(
    *,
    pack_root: Path | str,
    pack_id: str,
    plan_id: str,
    window_id: str,
    bracket_session_id: str,
    pre_attempt_id: str,
    post_attempt_id: str,
    claim_runs_root: Path | str,
    bound_runs_root: Path | str,
    custody_root: Path | str,
    night_dir: Path | str | None = None,
    pack_sha256: str | None = None,
    arm_decision_path: Path | str | None = None,
    boot_session_id: str | None = None,
) -> dict[str, Any]:
    """Write the window records and both runs-root locators, create-once.

    Order: ``authorization.json``, ``go.json``, ``launch.json`` under
    ``<custody_root>/window_lineage/``, then the claim locator, then the bound
    locator, each followed by its ``.sha256`` sidecar.  Every file is opened
    with O_EXCL and fsynced, then its directory is fsynced.  The roots must
    exist and be distinct; the driver creates them fresh for each attempt.

    Raises :class:`LineagePublicationError` only if a root or record cannot
    be written or the pack's inventory is unusable (every tagged member would
    then be refused, so the driver learns it before the chain starts).

    Values that are records, not inputs to the config check, never stop
    publication.  When the committed pack digest cannot be computed, the boot
    id cannot be read, or the arm decision file cannot be read, the lineage
    records ``null`` (go.json records no arm decision), ``launch.json`` lists
    the field and the error under ``unrecorded``, and
    :func:`audit_window_lineage` reports it.
    """

    try:
        pack = Path(pack_root).resolve(strict=True)
        claim = Path(claim_runs_root).resolve(strict=True)
        bound = Path(bound_runs_root).resolve(strict=True)
        custody = Path(custody_root).resolve(strict=True)
    except OSError as exc:
        raise LineagePublicationError(f"window root is unavailable: {exc}") from exc
    for label, root in (("claim", claim), ("bound", bound), ("custody", custody)):
        if not root.is_dir():
            raise LineagePublicationError(f"{label} root is not a directory: {root}")
    if claim == bound:
        raise LineagePublicationError("claim and bound runs roots must be distinct")
    night = Path(night_dir) if night_dir is not None else custody / "night"
    if not night.is_absolute():
        raise LineagePublicationError("night_dir must be absolute")
    try:
        plan_tree_raw = (pack / "plan_tree.json").read_bytes()
        plan_tree_sha256 = sha256_bytes(plan_tree_raw)
        config_inventory(pack, plan_tree_sha256)
    except (OSError, HazardLineageError) as exc:
        raise LineagePublicationError(f"pack inventory is unusable: {exc}") from exc

    # Records, not inputs to any collection-time check: an unavailable value
    # is written as null and listed, never a reason to lose the window.
    unrecorded: list[dict[str, str]] = []
    if pack_sha256 is None:
        try:
            pack_sha256 = committed_pack_sha256(pack)
        except Exception as exc:  # noqa: BLE001 - any digest failure is a records fact
            unrecorded.append({"field": "pack_sha256", "error": _describe(exc)})
    if pack_sha256 is not None and not _is_sha256(pack_sha256):
        unrecorded.append(
            {"field": "pack_sha256", "error": f"value is not a SHA-256: {pack_sha256!r}"}
        )
        pack_sha256 = None
    if boot_session_id is None:
        try:
            boot = current_boot_session_id()
        except Exception as exc:  # noqa: BLE001 - an unreadable boot is a records fact
            boot = None
            unrecorded.append({"field": "collection_boot_session_id", "error": _describe(exc)})
        else:
            if boot is None:
                unrecorded.append(
                    {
                        "field": "collection_boot_session_id",
                        "error": "kern.bootsessionuuid is unreadable",
                    }
                )
    else:
        boot = _canonical_boot(boot_session_id)
        if boot is None:
            unrecorded.append(
                {
                    "field": "collection_boot_session_id",
                    "error": f"value is not a UUID: {boot_session_id!r}",
                }
            )
    arm_decision: dict[str, str] | None = None
    if arm_decision_path is not None:
        try:
            decision_path = Path(arm_decision_path).resolve(strict=True)
            arm_decision = _reference(decision_path, decision_path.read_bytes())
        except OSError as exc:
            unrecorded.append({"field": "arm_decision", "error": _describe(exc)})

    records = custody / RECORDS_DIRNAME
    try:
        records.mkdir(exist_ok=True)
        authorization_path = records / AUTHORIZATION_RECORD_NAME
        authorization_raw = render_json(
            {
                "schema_version": AUTHORIZATION_SCHEMA,
                "purpose": HAZARD_PURPOSE,
                # Read only by run_campaign's block-limit reader, which needs
                # an integer >= 1 and applies no limit unless the purpose is
                # G2B_SHAKEDOWN.  HAZARD_PACK windows have no block limit.
                "permitted_blocks": 1,
                "block_limit_applies": False,
                "pack_id": pack_id,
                "plan_id": plan_id,
                "window_id": window_id,
            }
        )
        _write_once(authorization_path, authorization_raw)
        go_path = records / GO_RECORD_NAME
        go_raw = render_json(
            {
                "schema_version": GO_RECORD_SCHEMA,
                "arm_decision": arm_decision,
                "authorization": _reference(authorization_path, authorization_raw),
            }
        )
        _write_once(go_path, go_raw)
        launch_path = records / LAUNCH_RECORD_NAME
        launch_raw = render_json(
            {
                "schema_version": LAUNCH_RECORD_SCHEMA,
                "collection_boot_session_id": boot,
                "pack_id": pack_id,
                "plan_id": plan_id,
                "window_id": window_id,
                "go_receipt": _reference(go_path, go_raw),
                "unrecorded": unrecorded,
            }
        )
        _write_once(launch_path, launch_raw)
    except OSError as exc:
        raise LineagePublicationError(f"window records could not be written: {exc}") from exc

    lineage = {
        "schema_version": HAZARD_LINEAGE_SCHEMA,
        "collection_boot_session_id": boot,
        "pack_id": pack_id,
        "pack_sha256": pack_sha256,
        "plan_id": plan_id,
        "window_id": window_id,
        "bracket_session_id": bracket_session_id,
        "pack_root": str(pack),
        "plan_tree_sha256": plan_tree_sha256,
        "window_context": {
            "pre_attempt_id": pre_attempt_id,
            "post_attempt_id": post_attempt_id,
            "claim_runs_root": str(claim),
            "bound_runs_root": str(bound),
            "custody_root": str(custody),
            "night_dir": str(night),
        },
        "launch_record": _reference(launch_path, launch_raw),
    }
    try:
        validate_lineage(lineage)
    except HazardLineageError as exc:
        raise LineagePublicationError(f"lineage inputs are invalid: {exc}") from exc

    locators: dict[str, dict[str, str]] = {}
    try:
        for role, root in (("claim_runs_root", claim), ("bound_runs_root", bound)):
            raw = render_json(
                {
                    "schema_version": HAZARD_LOCATOR_SCHEMA,
                    "root_role": role,
                    "root_path": str(root),
                    "launch_lineage": lineage,
                }
            )
            path = root / LOCATOR_BASENAME
            _write_once(path, raw)
            _write_once(
                path.with_name(f"{LOCATOR_BASENAME}.sha256"),
                gnu_sidecar(sha256_bytes(raw), LOCATOR_BASENAME),
            )
            locators[role] = _reference(path, raw)
    except OSError as exc:
        raise LineagePublicationError(f"locator could not be written: {exc}") from exc
    return {
        "launch_lineage": copy.deepcopy(lineage),
        "locators": locators,
        "unrecorded": copy.deepcopy(unrecorded),
        "records": {
            "launch": lineage["launch_record"],
            "go": _reference(go_path, go_raw),
            "authorization": _reference(authorization_path, authorization_raw),
        },
    }


# ---------------------------------------------------------------------------
# Records audit (harvest): every formality is a finding, never a refusal


def _finding(
    code: str,
    detail: str,
    *,
    evidence: Sequence[Mapping[str, Any]] = (),
    scope: Mapping[str, Any] | None = None,
    family: str = "RECORDS",
    klass: str = "REPRESENTATION",
) -> dict[str, Any]:
    assert code in FINDING_CODES, code
    return {
        "code": code,
        "family": family,
        "klass": klass,
        "scope": dict(scope or {}),
        "detail": detail,
        "evidence": [dict(item) for item in evidence],
    }


def _evidence(path: Path) -> dict[str, Any]:
    try:
        return {"path": str(path), "sha256": sha256_bytes(path.read_bytes())}
    except OSError:
        return {"path": str(path), "sha256": None}


def _read_reference(
    reference: object, locate: Callable[[str], Path] = Path
) -> dict[str, Any] | None:
    """Return the referenced JSON object when its bytes match, else None."""

    if (
        not isinstance(reference, Mapping)
        or not isinstance(reference.get("path"), str)
        or not _is_sha256(reference.get("sha256"))
    ):
        return None
    try:
        raw = locate(reference["path"]).read_bytes()
        if sha256_bytes(raw) != reference["sha256"]:
            return None
        return _parse_object(raw)
    except (OSError, ValueError, RecursionError):
        return None


def _audit_locator(
    root: Path, role: str, findings: list[dict[str, Any]]
) -> tuple[Mapping[str, Any] | None, str | None]:
    path = root / LOCATOR_BASENAME
    scope = {"root_role": role}
    try:
        locator, digest = read_locator(path)
        raw = path.read_bytes()
    except (HazardLineageError, OSError) as exc:
        findings.append(
            _finding(
                "lineage.locator_unreadable",
                f"{role} locator: {exc}",
                evidence=[_evidence(path)],
                scope=scope,
            )
        )
        return None, None
    sidecar = path.with_name(f"{LOCATOR_BASENAME}.sha256")
    try:
        sidecar_ok = sidecar.read_bytes() == gnu_sidecar(digest, LOCATOR_BASENAME)
    except OSError:
        sidecar_ok = False
    if not sidecar_ok:
        findings.append(
            _finding(
                "lineage.locator_sidecar_mismatch",
                f"{role} locator sidecar is absent or does not match the locator bytes",
                evidence=[_evidence(path), _evidence(sidecar)],
                scope=scope,
            )
        )
    if raw != render_json(locator):
        findings.append(
            _finding(
                "lineage.locator_noncanonical",
                f"{role} locator bytes are not canonical JSON",
                evidence=[_evidence(path)],
                scope=scope,
            )
        )
    if locator["root_role"] != role:
        findings.append(
            _finding(
                "lineage.locator_role_differs",
                f"locator in the {role} records role {locator['root_role']}",
                evidence=[_evidence(path)],
                scope=scope,
            )
        )
    try:
        same_root = Path(locator["root_path"]).resolve() == root.resolve()
    except OSError:
        same_root = False
    if not same_root:
        findings.append(
            _finding(
                "lineage.locator_root_path_differs",
                f"{role} locator records root {locator['root_path']}, found at {root}",
                evidence=[_evidence(path)],
                scope=scope,
            )
        )
    return locator, digest


def audit_window_lineage(
    *,
    claim_runs_root: Path | str,
    bound_runs_root: Path | str,
    bundle_paths: Sequence[Path | str] = (),
) -> list[dict[str, Any]]:
    """Report every lineage formality that differs from what was published.

    Pure read; never raises for a records problem.  Each finding is
    ``{code, family, klass, scope, detail, evidence}``; the harvest wraps it
    into a ``joulewise.flag.v1`` record and the sealed catalog decides its
    effect.  An empty list means the records are exactly as published.

    Of ``bundle_paths``, a bundle whose ``config.json`` reads and carries no
    ``launch_lineage_required`` marker (a NEG-8 corpus or window-reference
    member) is unstamped by design, so its missing stamp is not a finding; a
    stamp it does carry is still compared.
    """

    findings: list[dict[str, Any]] = []
    roots = {"claim_runs_root": Path(claim_runs_root), "bound_runs_root": Path(bound_runs_root)}
    locators: dict[str, tuple[Mapping[str, Any], str]] = {}
    for role, root in roots.items():
        locator, digest = _audit_locator(root, role, findings)
        if locator is not None and digest is not None:
            locators[role] = (locator, digest)
    if len(locators) == 2:
        claim_lineage = locators["claim_runs_root"][0]["launch_lineage"]
        bound_lineage = locators["bound_runs_root"][0]["launch_lineage"]
        if render_json(claim_lineage) != render_json(bound_lineage):
            findings.append(
                _finding(
                    "lineage.sibling_lineage_differs",
                    "claim and bound locators carry different lineages",
                    evidence=[_evidence(root / LOCATOR_BASENAME) for root in roots.values()],
                )
            )
    if not locators:
        return findings
    lineage = next(iter(locators.values()))[0]["launch_lineage"]
    context = lineage["window_context"]
    for role, root in roots.items():
        try:
            same = Path(context[role]).resolve() == root.resolve()
        except OSError:
            same = False
        if not same:
            findings.append(
                _finding(
                    "lineage.context_root_differs",
                    f"lineage names {context[role]} as {role}; audited {root}",
                    scope={"root_role": role},
                )
            )
    def locate(recorded: str) -> Path:
        return _custody_path(recorded, context["custody_root"])

    launch = _read_reference(lineage["launch_record"], locate)
    go = _read_reference(launch.get("go_receipt"), locate) if launch else None
    authorization = _read_reference(go.get("authorization"), locate) if go else None
    if (
        launch is None
        or go is None
        or authorization is None
        or launch.get("schema_version") != LAUNCH_RECORD_SCHEMA
        or go.get("schema_version") != GO_RECORD_SCHEMA
        or authorization.get("schema_version") != AUTHORIZATION_SCHEMA
        or authorization.get("purpose") != HAZARD_PURPOSE
    ):
        findings.append(
            _finding(
                "lineage.record_chain_unverified",
                "launch -> go -> authorization records are absent or do not hash-verify",
                evidence=[_evidence(locate(lineage["launch_record"]["path"]))],
            )
        )
    elif go.get("arm_decision") is not None and _read_reference(go["arm_decision"], locate) is None:
        findings.append(
            _finding(
                "lineage.arm_decision_digest_differs",
                "the go record's arm-decision reference does not hash-verify",
                evidence=[_evidence(locate(str(go["arm_decision"].get("path"))))],
            )
        )
    # Values publication could not read (recorded null, listed in launch.json).
    notes: dict[str, str] = {}
    listed = launch.get("unrecorded") if isinstance(launch, Mapping) else None
    for item in listed if isinstance(listed, list) else ():
        if isinstance(item, Mapping) and item.get("field") in UNRECORDABLE_FIELDS:
            notes[str(item["field"])] = str(item.get("error"))
    if lineage["pack_sha256"] is None:
        findings.append(
            _finding(
                "lineage.pack_digest_unrecorded",
                "publication could not compute the committed pack digest; the pack-identity "
                "collector decides from preserved bytes: "
                + notes.get("pack_sha256", "no reason recorded"),
                evidence=[_evidence(locate(lineage["launch_record"]["path"]))],
            )
        )
    if lineage["collection_boot_session_id"] is None:
        findings.append(
            _finding(
                "lineage.collection_boot_unrecorded",
                "publication could not read kern.bootsessionuuid, so collection never compared "
                "boots; the harvest must establish the boot from the monitor journals: "
                + notes.get("collection_boot_session_id", "no reason recorded"),
                evidence=[_evidence(locate(lineage["launch_record"]["path"]))],
            )
        )
    if "arm_decision" in notes:
        findings.append(
            _finding(
                "lineage.arm_decision_unrecorded",
                "publication could not read the arm decision file: " + notes["arm_decision"],
                evidence=[_evidence(locate(lineage["launch_record"]["path"]))],
            )
        )
    plan_tree = Path(lineage["pack_root"]) / "plan_tree.json"
    observed = _evidence(plan_tree)["sha256"]
    if observed != lineage["plan_tree_sha256"]:
        finding = _finding(
            "lineage.plan_tree_digest_differs",
            "pack plan_tree.json bytes differ from the lineage's plan_tree_sha256",
            evidence=[_evidence(plan_tree)],
            family="PACK_IDENTITY",
            klass="NUMBER",
        )
        finding.update(observed=observed, expected=lineage["plan_tree_sha256"])
        findings.append(finding)
    night = locate(context["night_dir"])
    missing = [name for name in (CHAIN_EXITED_NAME, RESULT_NAME) if not (night / name).is_file()]
    if missing:
        findings.append(
            _finding(
                "lineage.completion_records_absent",
                f"driver records absent from {night}: {', '.join(missing)}",
            )
        )
    expected_lineage = render_json(lineage)
    for bundle in (Path(item) for item in bundle_paths):
        scope = {"bundle_path": str(bundle)}
        try:
            metadata = _parse_object((bundle / "metadata.json").read_bytes())
        except (OSError, ValueError, RecursionError):
            metadata = {}
        extra = metadata.get("extra") if isinstance(metadata.get("extra"), Mapping) else {}
        stamp = extra.get("launch_lineage")
        if not isinstance(stamp, Mapping) and _bundle_config_untagged(bundle):
            # The bundle writer stamps only marker-bearing configs
            # (bundle._writer_launch_lineage): an untagged member -- a NEG-8
            # corpus or window-reference bundle -- carries no stamp by design.
            continue
        if not isinstance(stamp, Mapping):
            findings.append(
                _finding(
                    "lineage.bundle_stamp_absent",
                    "bundle metadata carries no launch_lineage stamp",
                    evidence=[_evidence(bundle / "metadata.json")],
                    scope=scope,
                )
            )
            continue
        if render_json(stamp) != expected_lineage:
            findings.append(
                _finding(
                    "lineage.bundle_stamp_differs",
                    "bundle lineage stamp differs from the window's published lineage",
                    evidence=[_evidence(bundle / "metadata.json")],
                    scope=scope,
                )
            )
        root_locator = locators.get(
            "bound_runs_root"
            if roots["bound_runs_root"].resolve() == bundle.parent.resolve()
            else "claim_runs_root"
        )
        if root_locator is not None and extra.get("launch_lineage_locator_sha256") != root_locator[1]:
            findings.append(
                _finding(
                    "lineage.bundle_locator_digest_differs",
                    "bundle's recorded locator digest differs from its root's locator bytes",
                    evidence=[_evidence(bundle / "metadata.json")],
                    scope=scope,
                )
            )
    return findings


__all__ = [
    "AUTHORIZATION_SCHEMA",
    "FINDING_CODES",
    "GO_RECORD_SCHEMA",
    "HAZARD_LINEAGE_SCHEMA",
    "HAZARD_LOCATOR_SCHEMA",
    "HAZARD_PURPOSE",
    "HazardLineageError",
    "LAUNCH_RECORD_SCHEMA",
    "LOCATOR_BASENAME",
    "LineagePublicationError",
    "REASON_CODES",
    "ROOT_ROLES",
    "UNRECORDABLE_FIELDS",
    "audit_window_lineage",
    "authenticate_bundle",
    "authenticate_campaign",
    "authenticate_lineage",
    "committed_pack_sha256",
    "config_inventory",
    "current_boot_session_id",
    "is_hazard_lineage",
    "is_hazard_locator",
    "is_hazard_runs_root",
    "publish_window_lineage",
    "read_locator",
    "relocated_custody",
    "validate_lineage",
]
