"""RL-179 F-12 and RL-180's public contract and single-use publication boundary."""
from __future__ import annotations

import builtins
import hashlib
import json
import os
import re
from pathlib import Path
import sys
import traceback

from joulewise.cadence_looks import schema_check

TRIPWIRES = (
    "dev_included_below_45", "days_below_4", "cell_below_10",
    "start_reading_invalid_over_10pct", "hp01_below_9",
)
YES_NO = ("yes", "no")
THREE_WAY = (*YES_NO, "not_evaluable")
PUBLIC_WORDS = {
    "qualified_interim": THREE_WAY,
    **dict.fromkeys(TRIPWIRES, YES_NO),
    "drift_tripwire": ("within", "to_research_lead", "not_evaluable"),
    "twin_agrees": THREE_WAY,
    "stage2_error": ("no",),
}
BUILTIN_ERRORS = {cls: name for name, cls in vars(builtins).items()
                  if isinstance(cls, type) and issubclass(cls, BaseException)
                  and cls.__module__ == "builtins" and cls.__name__ == name}
ERROR_TYPES = frozenset((*BUILTIN_ERRORS.values(), "LinAlgError", "JSONDecodeError", "OtherError"))
SPENT_STATUSES = frozenset(("run", "frozen", "failed"))
FAILURE_STATUS = 1
PRIVATE_NAMES = frozenset(("coefficients.json", "fit.json", "step3.json", "twin.json", "stdout", "stderr"))


def dump(obj):
    """Canonical UTF-8 JSON with one trailing LF."""
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def public_record(look_id, manifest_sha, commit, stage1, stage1_sha, coefficient_sha, verdict, drift, twin):
    """Construct the report from the three decisions and authenticated artifact bindings."""
    tripwires = {}
    for key in TRIPWIRES:
        value = stage1["tripwires"][key]["trips"]
        if type(value) is not bool:
            raise ValueError("the stage-1 tripwires must be booleans")
        tripwires[key] = "yes" if value else "no"
    return {
        "look_id": look_id, "manifest_sha256": manifest_sha, "commit": commit,
        "stage1_sha256": stage1_sha, "coefficients_sha256": coefficient_sha,
        "in_energy_fit": stage1["counts"]["in_energy_fit"],
        "qualified_interim": {"passes": "yes", "fails": "no", "not_evaluable": "not_evaluable"}[verdict],
        **tripwires,
        "drift_tripwire": {"within": "within", "to the research lead": "to_research_lead",
                           "not_evaluable": "not_evaluable"}[drift],
        "twin_agrees": twin, "stage2_error": "no",
    }


def validate_public(record, schema, *, expected=None):
    fixed_fields = {"look_id", "manifest_sha256", "commit", "stage1_sha256", "coefficients_sha256", "in_energy_fit"}
    if (type(record) is not dict or record.keys() != fixed_fields | PUBLIC_WORDS.keys()
            or type(record["in_energy_fit"]) is not int or record["in_energy_fit"] < 0
            or record["look_id"] != "lm-interim-01"
            or any(record[key] not in words for key, words in PUBLIC_WORDS.items())
            or any(not isinstance(record[key], str) or not re.fullmatch(r"[a-f0-9]{%d}" % length, record[key])
                   for key, length in (("commit", 40), ("manifest_sha256", 64), ("stage1_sha256", 64),
                                       ("coefficients_sha256", 64)))
            or schema_check.errors(record, schema)):
        raise ValueError("the interim report violates the closed public schema")
    if expected is not None and record != expected:
        raise ValueError("the interim report differs from its authenticated sources")
    return record


def read_public(raw, schema):
    record = validate_public(json.loads(raw), schema)
    if dump(record) != raw:
        raise ValueError("the interim report is not canonical")
    return record


def failure_type(exc, linear_algebra_error):
    cls = type(exc)
    if cls is linear_algebra_error:
        return "LinAlgError"
    if cls is json.JSONDecodeError:
        return "JSONDecodeError"
    return BUILTIN_ERRORS.get(cls, "OtherError")


def write_private(path, payload):
    with path.open("xb") as out:
        out.write(payload)
        out.flush()
        os.fsync(out.fileno())


def sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_public(path, restricted, record, schema, *, expected):
    """Publish a complete, source-bound record without replacing any previous bytes."""
    payload = dump(validate_public(record, schema, expected=expected))
    pending = restricted / ".publication"
    write_private(pending, payload)
    if os.path.lexists(path):
        raise FileExistsError("the public report already exists")
    # Only the exclusive reservation holder publishes at this destination.
    # Rename exposes the complete bytes and removes the private temporary name in one operation.
    os.rename(pending, path)


def destinations(repo, row):
    """Resolve registered roots. Both look directories must already exist."""
    private_root = Path(row["custody_root"])
    public_root = Path(repo) / row["public_root"]
    if not private_root.is_absolute() or private_root.resolve() != private_root:
        raise ValueError("the registered custody root must be an absolute canonical directory")
    if public_root.resolve() != public_root or not public_root.is_relative_to(repo):
        raise ValueError("the registered public root must be a canonical repository directory")
    if private_root.is_relative_to(repo) or Path(repo).is_relative_to(private_root):
        raise ValueError("the registered custody root must be separate from the repository")
    private_parent = private_root / row["look_id"]
    public_parent = public_root / row["look_id"]
    if any(not path.is_dir() or path.is_symlink() for path in (private_parent, public_parent)):
        raise ValueError("the two registered look directories must already exist")
    restricted, public = private_parent / "RESTRICTED", public_parent / "PUBLIC.json"
    if os.path.lexists(restricted) or os.path.lexists(public):
        raise ValueError("the manifest id already has an execution reservation or public report")
    if private_parent.stat().st_dev != public_parent.stat().st_dev:
        raise ValueError("atomic publication requires the two registered roots on the same filesystem")
    return restricted, public


def run_reserved(restricted, execute, *, linear_algebra_error, keep_redirected=False):
    """Reserve the manifest ID and confine all subsequent process output."""
    sys.stdout.flush()
    sys.stderr.flush()
    saved = []
    redirected = False
    try:
        for fd in (1, 2):
            saved.append(os.dup(fd))
        restricted.mkdir(mode=0o700)
        try:
            for fd, name in ((2, "stderr"), (1, "stdout")):
                stream = os.open(restricted / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                try:
                    os.dup2(stream, fd)
                finally:
                    os.close(stream)
            redirected = True
            sync_directory(restricted.parent)
            execute()
        except BaseException as exc:
            if redirected:
                try:
                    traceback.print_exc()
                except Exception:
                    pass
            notice = f"stage2_error\n{failure_type(exc, linear_algebra_error)}\n".encode("ascii")
            os.write(saved[1], notice)
            return FAILURE_STATUS
        return 0
    finally:
        # The CLI stays redirected through interpreter shutdown. In-process synthetic callers recover their fds.
        if not keep_redirected or not redirected:
            try:
                if redirected:
                    sys.stdout.flush()
                    sys.stderr.flush()
            finally:
                for fd, original in enumerate(saved, 1):
                    os.dup2(original, fd)
        for original in saved:
            os.close(original)
