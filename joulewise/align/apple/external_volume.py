"""External log volume: mount census, arm check and write routing.

DRAFT amendment software (``docs/align/v4/DRAFT-AMENDMENT-external-log-volume.md``).
Nothing here is in force until the council and Ed adopt the amendment and the
hardware qualification in ``docs/align/v4/SSD-ALWAYS-ATTACHED-STUDY.md`` §6
passes. The default configuration (``status: "off"``) is today's rule: any
external volume mounted refuses the arm.

Three statuses:

* ``off`` (default): every external volume refuses. The allowlist is ignored.
* ``qualification``: only the allowlisted volume may be mounted, and it must
  pass every preparation check. Non-claim runs only (``claim_eligible`` is
  false in the verdict); this is the status the qualification session uses.
* ``active``: as ``qualification``, and the verdict is claim-eligible.

Fail-closed: a census that cannot be read, a ``diskutil``/``mdutil``/``tmutil``
answer that cannot be parsed, a second external volume, a network or disk
image mount, a volume that is not APFS, that has Spotlight indexing on, that
Time Machine does not exclude, whose fseventsd logging is on, or that ignores
ownership: each refuses. Nothing here writes to a volume or changes macOS
settings; ``prepare_plan`` only prints commands.

Routing (``route``) never places the custody root or ``TMPDIR`` (where the
powermetrics capture streams during measured segments) on the external
volume. ``log_mode`` chooses what may go there when the verdict passes:

* ``internal``: nothing (Option B of the study: attached, idle in windows).
* ``backup``: the per-member backup copies only, which ``run_campaign`` writes
  after a member ends, outside every measured segment (Option A-lite).
* ``direct``: the runs parent and the backups (Option A).

Any failed check routes everything internal and says why. ``RouteGuard`` is
the mid-window check: if the volume's device changes or disappears, every
later write goes internal for the rest of the window, and one
``external_volume.lost`` line is appended (fsync) to an internal journal.

Standard library only; every system call goes through an injectable runner.
"""
from __future__ import annotations

import json
import os
import plistlib
import re
import subprocess
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

SCHEMA = "joulewise.align_external_volume.v1"
VERDICT_SCHEMA = "joulewise.align_external_volume_verdict.v1"
STATUSES = ("off", "qualification", "active")
LOG_MODES = ("internal", "backup", "direct")
PRESENCE = ("attached",)
PASS, REFUSE = "PASS", "REFUSE"

DEFAULT_CONFIG: dict[str, Any] = {
    "schema": SCHEMA,
    "status": "off",
    "amendment": None,
    "allowlist": [],
    "mount_point": None,
    "log_mode": "internal",
    "subdir": "JouleWise",
    "expected_presence": "attached",
}
CONFIG_KEYS = frozenset(DEFAULT_CONFIG)

MOUNT_ARGV = ("/sbin/mount",)
DISKUTIL = "/usr/sbin/diskutil"
MDUTIL = "/usr/bin/mdutil"
TMUTIL = "/usr/bin/tmutil"
TIMEOUT_S = 30

UUID_RE = re.compile(r"^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$")
MOUNT_RE = re.compile(r"^(?P<device>.+?) on (?P<mount_point>/.*?) \((?P<options>[^()]*)\)$")
SUBDIR_RE = re.compile(r"^[A-Za-z0-9._-]+$")
# Pseudo filesystems every macOS boot mounts; they are not volumes.
PSEUDO_FS = frozenset({"devfs", "autofs", "nullfs", "fdesc"})

Runner = Callable[[Sequence[str]], "subprocess.CompletedProcess[str]"]
Exists = Callable[[str], bool]


class ConfigError(ValueError):
    """The external-volume configuration is malformed; treated as a refusal."""


def run_command(argv: Sequence[str]) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(list(argv), text=True, capture_output=True, check=False, timeout=TIMEOUT_S)


# ---------------------------------------------------------------- config


def validate_config(value: Mapping[str, Any] | None) -> dict[str, Any]:
    """The checked configuration; ``None`` gives the default (``off``)."""

    if value is None:
        return dict(DEFAULT_CONFIG)
    if not isinstance(value, Mapping):
        raise ConfigError("configuration must be a JSON object")
    unknown = set(value) - CONFIG_KEYS
    if unknown:
        raise ConfigError(f"unknown keys: {sorted(unknown)}")
    config = {**DEFAULT_CONFIG, **dict(value)}
    if config["schema"] != SCHEMA:
        raise ConfigError(f"schema must be {SCHEMA}")
    if config["status"] not in STATUSES:
        raise ConfigError(f"status must be one of {STATUSES}")
    if config["log_mode"] not in LOG_MODES:
        raise ConfigError(f"log_mode must be one of {LOG_MODES}")
    if config["expected_presence"] not in PRESENCE:
        raise ConfigError(f"expected_presence must be one of {PRESENCE}")
    if not isinstance(config["subdir"], str) or not SUBDIR_RE.match(config["subdir"]):
        raise ConfigError("subdir must be one plain path component")
    allowlist = config["allowlist"]
    if not isinstance(allowlist, list) or any(not isinstance(u, str) for u in allowlist):
        raise ConfigError("allowlist must be a list of volume UUID strings")
    if config["status"] == "off":
        return config
    if not isinstance(config["amendment"], str) or not config["amendment"].strip():
        raise ConfigError("a non-off status needs the amendment identifier")
    if len(allowlist) != 1 or not UUID_RE.match(allowlist[0]):
        raise ConfigError("a non-off status needs exactly one upper-case volume UUID")
    mount_point = config["mount_point"]
    if (not isinstance(mount_point, str) or not mount_point.startswith("/Volumes/")
            or "/" in mount_point[len("/Volumes/"):] or mount_point == "/Volumes/"):
        raise ConfigError("mount_point must be /Volumes/<name>")
    return config


def load_config(path: str | os.PathLike[str] | None) -> dict[str, Any]:
    if path is None:
        return validate_config(None)
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ConfigError(f"configuration unreadable: {exc}") from exc
    return validate_config(value)


# ---------------------------------------------------------------- census


def parse_mount(text: str) -> list[dict[str, Any]]:
    """``/sbin/mount`` lines as device, mount point, filesystem and options."""

    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = MOUNT_RE.match(line)
        if match is None:
            rows.append({"unparsed": line})
            continue
        options = [part.strip() for part in match["options"].split(",") if part.strip()]
        rows.append({"device": match["device"], "mount_point": match["mount_point"],
                     "fs_type": options[0].lower() if options else "", "options": options[1:]})
    return rows


def _diskutil_info(target: str, run: Runner) -> dict[str, Any]:
    result = run([DISKUTIL, "info", "-plist", target])
    if result.returncode != 0:
        raise ValueError(f"diskutil info {target} exit {result.returncode}")
    try:
        info = plistlib.loads(result.stdout.encode("utf-8"))
    except Exception as exc:  # plistlib raises several types
        raise ValueError(f"diskutil info {target} not a plist: {exc}") from exc
    if not isinstance(info, dict):
        raise ValueError(f"diskutil info {target} not a dictionary")
    return info


def census(run: Runner = run_command) -> dict[str, Any]:
    """Every mounted volume, classified internal, external or pseudo.

    A mount whose device is not ``/dev/disk*`` and whose filesystem is not a
    boot pseudo filesystem (network shares, FUSE, WebDAV) counts as external.
    A ``/dev/disk*`` mount counts as internal only when ``diskutil`` says
    ``Internal`` is true and it is not a disk image; anything unreadable is an
    error, and errors refuse.
    """

    errors: list[str] = []
    try:
        result = run(list(MOUNT_ARGV))
    except (OSError, subprocess.SubprocessError) as exc:
        return {"mounts": [], "external": [], "errors": [f"mount census failed: {exc}"]}
    if result.returncode != 0:
        return {"mounts": [], "external": [], "errors": [f"mount exit {result.returncode}"]}
    mounts = parse_mount(result.stdout)
    external = []
    for row in mounts:
        if "unparsed" in row:
            errors.append(f"unparsed mount line: {row['unparsed']}")
            continue
        if row["fs_type"] in PSEUDO_FS or row["device"] in ("devfs",):
            row["class"] = "pseudo"
            continue
        if not row["device"].startswith("/dev/disk"):
            row["class"] = "external"
            row["reason"] = "not a local disk device"
            external.append(row)
            continue
        try:
            info = _diskutil_info(row["device"], run)
        except (OSError, subprocess.SubprocessError, ValueError) as exc:
            errors.append(str(exc))
            row["class"] = "unmeasured"
            continue
        row["volume_uuid"] = info.get("VolumeUUID")
        row["volume_name"] = info.get("VolumeName")
        row["filesystem"] = info.get("FilesystemType")
        row["bus_protocol"] = info.get("BusProtocol")
        row["writable"] = info.get("WritableVolume")
        row["internal"] = info.get("Internal")
        # APFS volumes are synthesized ("Virtual") on internal and external
        # disks alike; only a disk image is never internal storage.
        virtual = info.get("BusProtocol") == "Disk Image"
        if info.get("Internal") is True and not virtual:
            row["class"] = "internal"
        elif info.get("Internal") is False or virtual:
            row["class"] = "external"
            external.append(row)
        else:
            errors.append(f"diskutil gave no Internal flag for {row['device']}")
            row["class"] = "unmeasured"
    return {"mounts": mounts, "external": external, "errors": errors}


# ---------------------------------------------------------------- checks


def _row(name: str, ok: bool, observed: Any) -> dict[str, Any]:
    return {"check": name, "ok": bool(ok), "observed": observed}


def spotlight_disabled(mount_point: str, run: Runner) -> tuple[bool, str]:
    result = run([MDUTIL, "-s", mount_point])
    text = (result.stdout or "") + (result.stderr or "")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    ok = result.returncode == 0 and "Indexing disabled." in lines and not any(
        "Indexing enabled" in line for line in lines)
    return ok, " | ".join(lines)


def time_machine_excluded(mount_point: str, run: Runner) -> tuple[bool, str]:
    result = run([TMUTIL, "isexcluded", mount_point])
    text = (result.stdout or "").strip()
    return result.returncode == 0 and text.startswith("[Excluded]"), text


def volume_checks(row: Mapping[str, Any], config: Mapping[str, Any], *, run: Runner = run_command,
                  exists: Exists = os.path.exists) -> list[dict[str, Any]]:
    """Preparation checks for the allowlisted volume; every row must be ok."""

    mount_point = row["mount_point"]
    options = list(row.get("options", ()))
    checks = [
        _row("uuid_allowlisted", row.get("volume_uuid") in config["allowlist"], row.get("volume_uuid")),
        _row("mount_point", mount_point == config["mount_point"], mount_point),
        _row("apfs", row.get("fs_type") == "apfs" and str(row.get("filesystem", "")).lower() == "apfs",
             [row.get("fs_type"), row.get("filesystem")]),
        _row("external_physical", row.get("internal") is False and row.get("bus_protocol") != "Disk Image",
             [row.get("internal"), row.get("bus_protocol")]),
        _row("writable", row.get("writable") is True and "read-only" not in options, row.get("writable")),
        _row("ownership_enabled", "noowners" not in options, options),
    ]
    try:
        ok, observed = spotlight_disabled(mount_point, run)
    except (OSError, subprocess.SubprocessError) as exc:
        ok, observed = False, f"mdutil failed: {exc}"
    checks.append(_row("spotlight_indexing_off", ok, observed))
    try:
        ok, observed = time_machine_excluded(mount_point, run)
    except (OSError, subprocess.SubprocessError) as exc:
        ok, observed = False, f"tmutil failed: {exc}"
    checks.append(_row("time_machine_excluded", ok, observed))
    checks.append(_row("fseventsd_no_log", exists(os.path.join(mount_point, ".fseventsd", "no_log")),
                       ".fseventsd/no_log"))
    return checks


def advisory(row: Mapping[str, Any], *, exists: Exists = os.path.exists) -> list[dict[str, Any]]:
    """Recorded, never judged: macOS may ignore the marker and remount options."""

    mount_point = row["mount_point"]
    return [_row("metadata_never_index_marker", exists(os.path.join(mount_point, ".metadata_never_index")),
                 ".metadata_never_index"),
            _row("noatime", "noatime" in row.get("options", ()), row.get("options", []))]


def arm_check(config: Mapping[str, Any], census_result: Mapping[str, Any], *, run: Runner = run_command,
              exists: Exists = os.path.exists) -> dict[str, Any]:
    """PASS or REFUSE for the external-volume rule, with every reason."""

    reasons: list[str] = []
    rows: list[dict[str, Any]] = []
    notes: list[dict[str, Any]] = []
    reasons += [f"census_unmeasured:{error}" for error in census_result.get("errors", [])]
    external = list(census_result.get("external", []))
    status = config["status"]
    if status == "off":
        reasons += [f"external_volume_mounted:{row.get('mount_point')}" for row in external]
    else:
        allowed = [row for row in external if row.get("volume_uuid") in config["allowlist"]]
        reasons += [f"external_volume_not_allowlisted:{row.get('mount_point')}"
                    for row in external if row not in allowed]
        if len(allowed) > 1:
            reasons.append("allowlisted_volume_mounted_more_than_once")
        if not allowed and config["expected_presence"] == "attached":
            reasons.append("allowlisted_volume_absent")
        if len(allowed) == 1:
            rows = volume_checks(allowed[0], config, run=run, exists=exists)
            notes = advisory(allowed[0], exists=exists)
            reasons += [f"volume_check_failed:{row['check']}" for row in rows if not row["ok"]]
    verdict = PASS if not reasons else REFUSE
    return {"schema": VERDICT_SCHEMA, "verdict": verdict, "status": status,
            "amendment": config.get("amendment"), "log_mode": config["log_mode"],
            "claim_eligible": verdict == PASS and status == "active",
            "reasons": reasons, "checks": rows, "advisory": notes,
            "external": [{k: row.get(k) for k in ("device", "mount_point", "fs_type", "volume_uuid",
                                                    "volume_name", "bus_protocol")} for row in external]}


# ---------------------------------------------------------------- routing


def route(config: Mapping[str, Any], verdict: Mapping[str, Any], *, internal_session_root: str | os.PathLike[str],
          session_id: str) -> dict[str, Any]:
    """Where each window write goes. Custody and TMPDIR are always internal."""

    if not isinstance(session_id, str) or not SUBDIR_RE.match(session_id):
        raise ConfigError("session_id must be one plain path component")
    internal = Path(internal_session_root)
    paths = {"custody_root": internal / "custody", "tmpdir": internal / "tmp",
             "runs_parent": internal / "runs-parent", "claim_backup": internal / "backup-claim",
             "bound_backup": internal / "backup-bound"}
    fallback = None
    external_used = False
    mode = config["log_mode"]
    if config["status"] == "off":
        fallback = "status_off"
    elif verdict.get("verdict") != PASS:
        fallback = "arm_check_refused"
    elif mode == "internal":
        fallback = None
    else:
        base = Path(config["mount_point"]) / config["subdir"] / session_id
        paths["claim_backup"] = base / "backup-claim"
        paths["bound_backup"] = base / "backup-bound"
        if mode == "direct":
            paths["runs_parent"] = base / "runs-parent"
        external_used = True
    return {"schema": SCHEMA + ".route", "log_mode": mode, "status": config["status"],
            "external_used": external_used, "fallback": fallback,
            "paths": {k: str(v) for k, v in paths.items()},
            "internal_fallback": {"runs_parent": str(internal / "runs-parent"),
                                  "claim_backup": str(internal / "backup-claim"),
                                  "bound_backup": str(internal / "backup-bound")},
            "mount_point": config.get("mount_point")}


class RouteGuard:
    """Mid-window presence check; a lost volume routes the rest internal.

    ``bind`` records the mount point's device at arm. ``target(kind)`` returns
    the path to write ``kind`` to now. The check is a ``stat`` of the mount
    point only (no ``diskutil``/``mdutil`` call), so it does not wake a
    sleeping drive or start metadata work. Once lost, a window never switches
    back to the external volume, even if it reappears.
    """

    def __init__(self, routed: Mapping[str, Any], *, journal_path: str | os.PathLike[str],
                 stat: Callable[[str], Any] = os.stat, now: Callable[[], float] = time.time):
        self.routed = routed
        self.journal_path = Path(journal_path)
        self._stat = stat
        self._now = now
        self.lost: str | None = None
        self.device: int | None = None
        mount_point = routed.get("mount_point")
        if mount_point and self.journal_path.is_relative_to(mount_point):
            raise ConfigError("the route journal must be internal")
        if routed.get("external_used"):
            try:
                self.device = self._stat(str(mount_point)).st_dev
                parent = self._stat(os.path.dirname(str(mount_point))).st_dev
            except OSError as exc:
                self._lose(f"stat failed at bind: {exc}")
            else:
                if self.device == parent:
                    self._lose("mount point is not a mounted volume at bind")

    def _lose(self, reason: str) -> None:
        if self.lost is not None:
            return
        self.lost = reason
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps({"schema": SCHEMA + ".journal", "kind": "external_volume.lost",
                           "reason": reason, "epoch_s": self._now(),
                           "mount_point": self.routed.get("mount_point")}, sort_keys=True)
        with self.journal_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def check(self) -> bool:
        """True while the external route is healthy (or was never used)."""

        if not self.routed.get("external_used"):
            return True
        if self.lost is not None:
            return False
        mount_point = str(self.routed["mount_point"])
        try:
            device = self._stat(mount_point).st_dev
            parent = self._stat(os.path.dirname(mount_point)).st_dev
        except OSError as exc:
            self._lose(f"stat failed: {exc}")
            return False
        if device != self.device or device == parent:
            self._lose("mount point device changed or volume unmounted")
            return False
        return True

    def target(self, kind: str) -> str:
        paths = self.routed["paths"]
        if kind not in paths:
            raise KeyError(kind)
        if kind in self.routed["internal_fallback"] and not self.check():
            return self.routed["internal_fallback"][kind]
        return paths[kind]


# ---------------------------------------------------------------- preparation (print only)


DEVICE_RE = re.compile(r"^disk[0-9]+$")


def prepare_plan(device: str, *, name: str = "JW-EXT") -> list[str]:
    """The preparation commands, for a human to run. Never executed here."""

    if not DEVICE_RE.match(device) or device in ("disk0", "disk1", "disk2", "disk3"):
        raise ConfigError("device must be an external whole-disk identifier such as disk6 "
                          "(disk0-disk3 are the internal SSD and its synthesized containers)")
    if not re.match(r"^[A-Za-z0-9-]{1,27}$", name):
        raise ConfigError("volume name must be 1-27 letters, digits or hyphens")
    mp = f"/Volumes/{name}"
    return [
        "# DRY RUN. Nothing below has been executed. Run on the measurement Mac by day,",
        "# with no window armed, step by step, checking each output.",
        "# 1. Identify the drive and SHOW ED WHAT IS ON IT before any erase.",
        "diskutil list external physical",
        f"diskutil info /dev/{device}",
        f"diskutil list /dev/{device}",
        "#    (if it already holds an APFS volume, list it: ls -la /Volumes/<existing name>)",
        "# 2. Only if Ed confirms, and only if it is not already APFS named " + name + ":",
        f"#    diskutil eraseDisk APFS {name} GPT /dev/{device}      # DESTROYS ALL DATA ON {device}",
        "# 3. Spotlight off for the volume (authoritative), plus the legacy marker.",
        f"sudo mdutil -i off {mp}",
        f"sudo mdutil -E {mp}",
        f"sudo touch {mp}/.metadata_never_index",
        f"mdutil -s {mp}                     # expect: Indexing disabled.",
        "#    Also add the volume in System Settings > Spotlight > Search Privacy.",
        "# 4. fseventsd logging off for the volume; takes effect at the next mount.",
        f"sudo mkdir -p {mp}/.fseventsd && sudo touch {mp}/.fseventsd/no_log",
        "# 5. Time Machine: exclude the volume and stop new-disk prompts.",
        f"sudo tmutil addexclusion -v {mp}",
        "sudo defaults write /Library/Preferences/com.apple.TimeMachine DoNotOfferNewDisksForBackup -bool YES",
        f"tmutil isexcluded {mp}              # expect: [Excluded]",
        "# 6. Honour file ownership (custody modes depend on it).",
        f"sudo diskutil enableOwnership {mp}",
        "# 7. Remount so fseventsd and ownership take effect, then record the UUID.",
        f"diskutil unmount {mp} && diskutil mount {device}s1   # check the APFS volume id with diskutil list",
        f"diskutil info -plist {mp} | plutil -extract VolumeUUID raw -",
        "#    Put that UUID (upper case) in configs/align/v4/external_log_volume.json allowlist.",
        "# 8. Record (do not change) the power settings the readiness probes pin.",
        "pmset -g custom",
        "# 9. Verify with the arm check in qualification status.",
        "python3 scripts/align_external_volume.py arm-check --config <qualification config>",
    ]
