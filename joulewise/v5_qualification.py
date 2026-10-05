"""Shared custody and structural-output boundaries for block-4 harvests.

Collected bytes are never edited. Replay uses original absolute locators;
copies, diagnostics and transcripts live behind a mode-0700 custody directory.
This module owns no G-gate, calibration, battery or reduction acceptance rule.
"""
from __future__ import annotations

import contextlib
import io
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

from joulewise import arm_readiness as readiness, night_gate
from joulewise.measurement_liveness import pending_launch_closed, observe_identity, _start_token
from scripts.harvest_g2a_window import archive, sha
from scripts.harvest_window import inventory


BATTERY_BOUNDARY_PHASES = {"arm": "arm_check", "publication": "publish_install", "t0": "t0"}


class HarvestRefusal(ValueError):
    """Only fixed structural codes may cross the public boundary."""


def read(path):
    path = Path(path)
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise HarvestRefusal("input_not_regular")
    return readiness.parse_json_bytes(path.read_bytes())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(readiness.render_json(value))


def identifier(value):
    if not isinstance(value, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value) is None:
        raise HarvestRefusal("identity_invalid")
    return value


def authenticated_reference(value):
    if not isinstance(value, dict) or set(value) != {"path", "sha256"}:
        raise HarvestRefusal("locator_invalid")
    path = Path(value["path"])
    if not path.is_absolute() or any(p.is_symlink() for p in (path, *path.parents)):
        raise HarvestRefusal("locator_invalid")
    if not path.is_file() or sha(path) != value["sha256"]:
        raise HarvestRefusal("locator_digest_mismatch")
    return path


def reference(path):
    return {"path": str(path), "sha256": sha(path)}


def s1_desk_records(bundle):
    """Require the four post-STOP observations, each bound by its lifecycle hash."""
    from joulewise import t0_rehearsal as t0
    lifecycle = bundle.record("lifecycle")
    if lifecycle is None or not isinstance(lifecycle.value, dict):
        raise HarvestRefusal("s1_desk_lifecycle_missing")
    stages = lifecycle.value.get("stages", [])
    result = {}
    for name in ("claim_backup", "bound_backup", "close_out", "restore"):
        rows = [row for row in stages if row.get("stage_id") == name]
        if len(rows) != 1 or rows[0].get("status") != "COMPLETE":
            raise HarvestRefusal("s1_desk_stage_missing")
        try:
            artifact = t0._verify_artifact_reference(bundle, rows[0].get("evidence"), label=name)
        except ValueError as exc:
            raise HarvestRefusal("s1_desk_stage_digest_mismatch") from exc
        if (not isinstance(artifact.value, dict) or artifact.value.get("schema_version") != t0.QUALIFICATION_STAGE_SCHEMA
                or artifact.value.get("stage_id") != name):
            raise HarvestRefusal("s1_desk_stage_schema_invalid")
        result[name] = {"path": str(artifact.path), "sha256": artifact.sha256}
    return result


def group_clear(night, *, killpg=os.killpg, plan_id=None, observer=None):
    """Read #475 custody even if the PASS-only chain marker was never made.

    Do not write launch.resolved: absence is recorded in the derived harvest.
    A dead leader alone is insufficient to disprove a surviving process group.
    """
    night = Path(night)
    pending = night / "launch.pending"
    if pending.exists() or pending.is_symlink():
        value = read(pending)
        if (set(value) != {"schema", "pgid", "pid", "start_time", "plan_id", "attempt_id", "epoch_s"}
                or value["schema"] != "joulewise.launch_pending.v1"
                or type(value["pid"]) is not int or value["pid"] <= 1
                or value["pgid"] != value["pid"]
                or not isinstance(value["start_time"], (str, type(None)))
                or not isinstance(value["attempt_id"], str) or not value["attempt_id"]
                or type(value["epoch_s"]) not in (int, float)
                or (plan_id is not None and value["plan_id"] != plan_id)):
            raise HarvestRefusal("pending_launcher_identity_invalid")
        if pending_launch_closed(night):
            resolved = night / "launch.resolved"
            if resolved.exists() and read(resolved)["pgid"] != value["pgid"]:
                raise HarvestRefusal("pending_launcher_closure_mismatch")
            return True
        identity = (observer or observe_identity)(value["pid"])
        recorded, current = _start_token(value["start_time"]), _start_token(identity.start_time)
        if identity.state == "LIVE" and recorded is not None and current is not None and recorded != current:
            return True
        pgid = value["pgid"]
    else:
        started = night / "chain.started"
        if not started.exists() and not started.is_symlink():
            return True
        pgid = read(started).get("pgid")
        if type(pgid) is not int or pgid <= 1:
            raise HarvestRefusal("chain_group_identity_invalid")
    try:
        killpg(pgid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return False


def g10_sources(custody):
    """Preserve the complete original physical-control tree for harvest replay."""
    record_path = Path(custody) / "qualification-plan-record.json"
    if not record_path.exists():
        return {}
    prereqs = read(record_path)["prerequisites"]
    positive = authenticated_reference(prereqs["g10_control"])
    manifests = prereqs["g10_artifacts"]
    if len(manifests) != 1:
        raise HarvestRefusal("g10_custody_manifest_required")
    manifest = authenticated_reference(manifests[0])
    if manifest.name != "custody-manifest.json" or positive != manifest.parent / "positive-control.json":
        raise HarvestRefusal("g10_custody_locator_invalid")
    return {"g10-custody": manifest.parent}


def replay_g10_custody(custody, positive):
    """Re-run G10's native verifier with the registered head/boot/order bounds."""
    from scripts.ed_session.capture_t0_anchor_positive_control import verify_g10_custody
    record = read(Path(custody) / "qualification-plan-record.json")
    prereqs = record["prerequisites"]
    positive_path = authenticated_reference(prereqs["g10_control"])
    manifest_path = authenticated_reference(prereqs["g10_artifacts"][0])
    if read(positive_path) != positive:
        raise HarvestRefusal("g10_positive_copy_mismatch")
    first = read(authenticated_reference(prereqs["a1_control"]))
    observation = read(authenticated_reference(first["observation"]))
    plan = read(authenticated_reference(record["plan"]))
    verify_g10_custody(positive_path, manifest_path, code_root=Path(plan["measurement_root"]),
        head=record["head"], before_monotonic_ns=observation["first_t0_boundary_monotonic_ns"],
        boot_id=first["boot_session_id"].lower())
    # The bundle carries an exact duplicate for custody, while replay retains
    # original absolute locators embedded by the live producer.
    retained = Path(custody) / "records/g10-custody" / manifest_path.parent.name
    if census_sources({"tree": retained}) != census_sources({"tree": manifest_path.parent}):
        raise HarvestRefusal("g10_retained_tree_mismatch")
    return {"path": str(manifest_path), "sha256": sha(manifest_path)}


def require_terminal_boundary(plan, terminal):
    """The chain writes STOP at one plan-bound path, never a supplied substitute."""
    expected = Path(plan.custody_root) / "night/transcript/post-bracket-terminal-boundary.json"
    record = read(Path(plan.custody_root) / "qualification-plan-record.json")
    if record.get("terminal_boundary_path") != str(expected) or Path(terminal) != expected:
        raise HarvestRefusal("terminal_boundary_path_mismatch")
    if list(Path(plan.custody_root).rglob("post-bracket-terminal-boundary.json")) != [expected]:
        raise HarvestRefusal("terminal_boundary_census_invalid")


def off_receipt_path(plan, night_dir=None):
    """Match capture_t0_step's pack custody and the diagnostic night layout."""
    from joulewise import network_time_off
    night = Path(night_dir) if night_dir is not None else Path(plan.custody_root) / "night"
    if plan.receipt_class == "TRANSACTION_PACK":
        return night.parent / identifier(plan.pack_night["pack_id"]) / "arm_readiness.t0.inputs" / network_time_off.RECEIPT_BASENAME
    return night / network_time_off.RECEIPT_BASENAME


def pin_only_head_extension(repository, armed_head, head):
    """Authenticate H_pin from Git objects without changing the live checkout."""
    if any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value)
           for value in (armed_head, head)):
        raise ValueError("Phase G invalid head identity")
    command = ["git", "-C", str(repository)]
    if head == armed_head:
        return None
    if subprocess.run(command + ["merge-base", "--is-ancestor", armed_head, head],
                      capture_output=True, check=False).returncode != 0:
        raise ValueError("Phase G head is not descended from the armed head")
    try:
        changed = subprocess.check_output(command + ["diff", "--name-only", armed_head, head],
                                          text=True, stderr=subprocess.PIPE).splitlines()
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError("Phase G head extension is unavailable") from error
    if changed != ["configs/calibration/calibration_ledger_head.json"]:
        raise ValueError("Phase G head extension is not pin-only")
    try:
        raw = subprocess.check_output(command + ["show", head + ":" + changed[0]], stderr=subprocess.PIPE)
        pin = readiness.parse_json_bytes(raw)
    except (OSError, subprocess.CalledProcessError, readiness.ArmReadinessError) as error:
        raise ValueError("Phase G head extension pin is unavailable") from error
    from joulewise.calibration_ledger import LEDGER_SCHEMA, _head_pin
    if (not isinstance(pin, dict) or pin.get("ledger_schema") != LEDGER_SCHEMA
            or _head_pin(pin) is None):
        raise ValueError("Phase G head extension pin is malformed")
    return {"armed_head": armed_head, "head": head, "changed_paths": changed,
            "terminal_head_pin": pin}


def load_plan(path, purpose, *, now=time.time, clear=group_clear):
    from scripts.run_night import WINDOW_SHUTDOWN_GRACE_S
    plan = night_gate.NightPlan.from_mapping(read(path))
    custody = Path(plan.custody_root)
    if Path(path).absolute().parent != custody or plan.receipt_class != "TRANSACTION_PACK":
        raise HarvestRefusal("qualification_plan_identity_invalid")
    records = night_gate._authenticate_pack_records(plan)
    authorization = records["authorization_record"]
    if (authorization["purpose"] != purpose or authorization["claim_eligible"] is not False
            or authorization["permitted_blocks"] != 1):
        raise HarvestRefusal("qualification_plan_identity_invalid")
    chain = Path(plan.chain_path)
    if sha(chain) != Path(plan.chain_sha256_path).read_text().split()[0]:
        raise HarvestRefusal("chain_digest_mismatch")
    if now() < plan.t0_epoch_s + plan.window_max_s + WINDOW_SHUTDOWN_GRACE_S:
        raise HarvestRefusal("harvest_before_completion_boundary")
    night = custody / "night"
    if not (night / "courier.sent").is_file() or not clear(night, plan_id=plan.plan_id):
        raise HarvestRefusal("delivery_missing_or_launcher_group_alive")
    return plan


def census_sources(sources):
    result = {}
    for name, path in sources.items():
        path = Path(path).absolute()
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise HarvestRefusal("source_symlink")
        rows = inventory(path)
        if any("link" in row for row in rows.values()):
            raise HarvestRefusal("source_symlink")
        result[name] = rows
    return result


def tree_hash(root):
    import hashlib
    rows = census_sources({"tree": root})["tree"]
    raw = "".join(f"{name}\0{row['sha256']}\n" for name, row in sorted(rows.items()) if "sha256" in row)
    return hashlib.sha256(raw.encode()).hexdigest()


def archive_sources(sources, destination, *, previous=None, added=()):
    destination = Path(destination).absolute()
    if destination.exists() or any(destination == Path(p) or Path(p) in destination.parents
                                   or destination in Path(p).parents for p in sources.values()):
        raise HarvestRefusal("archive_exists_or_overlaps_source")
    original = census_sources(sources)
    if previous is not None:
        old = read(Path(previous) / "replay-locators.json")
        expected = {row["name"]: row for row in old["sources"]}
        current_names = set(sources) - set(added)
        if current_names != set(expected):
            raise HarvestRefusal("reharvest_source_census_changed")
        for name in current_names:
            if (str(sources[name]) != expected[name]["original_path"]
                    or original[name] != expected[name]["inventory"]):
                raise HarvestRefusal("reharvest_source_bytes_changed")
    destination.mkdir(parents=True)
    restricted = destination / "withheld"
    restricted.mkdir(mode=0o700)
    archived = archive(sources, restricted / "sources")
    locators = {"schema": "joulewise.v5_qualification_replay_locators.v1", "sources": [
        {"name": name, "original_path": str(path), "archived_path": str(restricted / "sources" / name),
         "inventory": archived[name]} for name, path in sorted(sources.items())]}
    write(destination / "replay-locators.json", locators)
    # Hash/path census is public; source bytes stay in restricted custody.
    sums = (restricted / "sources/SHA256SUMS").read_text()
    (destination / "SHA256SUMS").write_text("".join(
        f"{digest}  withheld/sources/{name}\n"
        for digest, name in (line.split("  ", 1) for line in sums.splitlines())))
    return original


def unchanged(sources, original):
    if census_sources(sources) != original:
        raise HarvestRefusal("source_tree_mutated")


def captured_call(function, transcript, *args, **kwargs):
    """Never echo validator messages, nested diagnostics or unfiltered log tails."""
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            return function(*args, **kwargs)
    finally:
        Path(transcript).parent.mkdir(parents=True, exist_ok=True)
        with Path(transcript).open("x") as stream:
            stream.write(out.getvalue())
            stream.write(err.getvalue())


def captured_battery_observation(path):
    """Read a native battery observation from a capture or the T-0 C3 receipt."""
    from joulewise import battery_float
    value = read(path)
    if value.get("schema") == battery_float.SCHEMA:
        observation = value
    else:
        candidates = [row.get("measured", {}).get("battery_float") for row in value.get("conditions", [])
                      if row.get("condition_id") == "C3" and "battery_float" in row.get("measured", {})]
        if len(candidates) != 1:
            raise HarvestRefusal("t0_battery_capture_missing")
        observation = candidates[0]
    stdout = observation.get("raw_stdout")
    if not isinstance(stdout, str):
        raise HarvestRefusal("t0_battery_raw_missing")
    raw = stdout.encode("utf-8")
    if readiness.sha256_bytes(raw) != observation.get("raw_stdout_sha256"):
        raise HarvestRefusal("t0_battery_raw_mismatch")
    return observation, raw


def persist_battery_observation(directory, name, observation, raw):
    """Retain the exact observed stdout even when the predicate refuses."""
    if not isinstance(raw, bytes) or readiness.sha256_bytes(raw) != observation.get("raw_stdout_sha256"):
        raise HarvestRefusal("battery_boundary_raw_mismatch")
    directory = Path(directory)
    if any(path.is_symlink() for path in (directory, *directory.parents)):
        raise HarvestRefusal("battery_boundary_directory_symlink")
    directory.mkdir(parents=True, exist_ok=True)
    raw_path, record_path = directory / (name + ".ioreg"), directory / (name + ".json")
    for path, body in ((raw_path, raw), (record_path, readiness.render_json(observation))):
        with path.open("xb") as stream:
            os.chmod(path, 0o600)
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
    return {"record": reference(record_path.absolute()), "raw": reference(raw_path.absolute())}


def battery_boundaries(path, digest, plan_id):
    """Authenticate recorded #421 boundary probes with the shared raw parser."""
    from joulewise import battery_float
    authenticated_reference({"path": str(path), "sha256": digest})
    value = read(path)
    if (value.get("schema") != "joulewise.v5_qualification_battery_boundaries.v1"
            or value.get("plan_id") != plan_id
            or set(value.get("observations", {})) != {"arm", "publication", "t0"}):
        raise HarvestRefusal("battery_boundary_census_invalid")
    passed = True
    for role, item in value["observations"].items():
        stored = read(authenticated_reference(item["record"]))
        raw = authenticated_reference(item["raw"]).read_bytes()
        if (stored.get("raw_stdout_sha256") != readiness.sha256_bytes(raw)
                or stored.get("plan_id") != plan_id
                or stored.get("schema") != battery_float.SCHEMA
                or stored.get("phase") != BATTERY_BOUNDARY_PHASES[role]):
            raise HarvestRefusal("battery_boundary_digest_or_identity_mismatch")
        if "source_capture" in stored:
            capture = authenticated_reference(stored["source_capture"])
            observed, original = captured_battery_observation(capture)
            if {k: v for k, v in stored.items() if k != "source_capture"} != observed or original != raw:
                raise HarvestRefusal("battery_boundary_capture_mismatch")
        if stored.get("probe_error") or stored.get("timed_out") or stored.get("exit_code") != 0 or stored.get("argv") != list(battery_float.IOREG_BATTERY_ARGV):
            passed = False
            continue
        try:
            parsed = battery_float.parse(raw, stored["wall_time_s"])
        except ValueError:
            passed = False
            continue
        if any(stored.get(key) != val for key, val in parsed.items()):
            raise HarvestRefusal("battery_boundary_replay_mismatch")
        passed = passed and parsed["passed"]
    return passed


def disposition(occurrence, verdict, cause_classes, majority=None):
    # A RECOVER without an already reviewed named cure is END STATE. A later
    # explicit lead authority binds the one allowed s2; no automatic retry.
    end = verdict == "RECOVER"
    # Eligibility is a prospective lead decision, never automatic permission.
    return {"end_state": end, "s2_eligible": False,
            "next_step": ("design_consult_cold_gate" if end else
                          "r3_cure_and_head_coverage_required" if verdict == "RECOVER" else
                          "identical_byte_reharvest" if verdict == "REFUSED" else
                          "fresh_plan_after_cause_removed" if verdict == "NULL" else "lead_ratification")}


def publish(destination, record):
    """Record is constructed field-by-field; never merge an evaluator document."""
    write(Path(destination) / "harvest.json", record)
    return record


def public_print(record):
    print(f"verdict={record['verdict']}")


def preflight_refusal(schema, scratch=Path("/tmp/dd5-fold")):
    """G2-a's safe fallback: never write into an unsafe archive coordinate."""
    scratch = Path(scratch).resolve()
    scratch.mkdir(parents=True, exist_ok=True)
    destination = Path(tempfile.mkdtemp(prefix="v5-harvest-refusal-", dir=scratch))
    record = {"schema": schema, "verdict": "REFUSED", "cause_classes": ["tooling"],
              "cause_codes": ["completion_ownership_archive_or_authentication_fault"],
              "s2_eligible": False, "end_state": False, "next_step": "r3_identical_byte_reharvest"}
    publish(destination, record)
    public_print(record)
    print(f"harvest={destination / 'harvest.json'} sha256={sha(destination / 'harvest.json')}")
    return record


def release_metrics(*args, **kwargs):
    # Qualification PASS is deliberately incapable of releasing measurements.
    raise HarvestRefusal("claim_plan_seal_and_lead_release_required")


def boundary_sources(path):
    value = read(path)
    sources = {"battery-boundary-map": path}
    for role, item in value.get("observations", {}).items():
        identifier(role)
        for kind in ("record", "raw"):
            sources[f"battery-{role}-{kind}"] = authenticated_reference(item[kind])
        stored = read(sources[f"battery-{role}-record"])
        if "source_capture" in stored:
            sources[f"battery-{role}-capture"] = authenticated_reference(stored["source_capture"])
    return sources
