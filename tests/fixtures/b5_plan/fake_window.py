"""Mock-runtime fixtures for the block-5 HAZARD_PACK lane (L2) tests.

A fake measurement checkout links the three committed v5 packs and their
auxiliary corpora (read-only symlinks) and replaces every tool the chain
runs -- the bracket reserver, the fiducial capture, the campaign runner and
the ledger status reader -- with a small stdlib script that records its argv
and writes the files the real tool would leave behind. Only those hardware
seams are fake: the plan writer, the chain bytes, the zsh run and the driver
are the production code.

Each fake reads ``fake-behavior.json`` in the checkout:

``reservation_rc``      exit code of the reservation (0)
``capture_rc``          {"pre": rc, "post": rc} of the fiducial capture
``b_fiducial_s``        the pre-calibration fiducial bound written (0.03)
``fail_run_ids``        members the campaign runner fails
``neg8_minimum_n``      the derivation's minimum (whole_window.NEG8_DRIFT_MINIMUM_N)
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKS = {
    "alpha": "d117_floor_qwen3-1p7b_v5",
    "beta": "d117_floor_qwen3-8b_v5",
    "gamma": "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5",
}
AUXILIARY_PACKS = ("neg8_reference_corpus_v5", "window_references_v5")
# Block 4's committed sizing adapter output; its T_stream_max allowance is the
# X10 sizing value the clock gate uses (335 s).
SIZING_PACK = "v5_qualification_25g83"
SIZING_ALLOWANCES = REPO_ROOT / "configs/campaigns" / SIZING_PACK / "sizing_allowances.json"
# A fixture sizing output for the programmed span (block 5's own sizing output
# is FILL[B5-SPAN-AND-WINDOW-MAX] in the registration draft).
FIXTURE_SIZING_RELATIVE = "configs/sizing/b5_fixture_sizing.json"
FIXTURE_SIZING = {"schema_version": "fixture.b5_sizing.v1", "totals": {"programmed_span_s": 3600}}
# Lane L1's threshold contract (joulewise.hazards.arm.default_thresholds() at
# L1 5fa6ddcf), injected into the plan writer here because L1's package lands
# at integration; tests/test_b5_plan.py checks it against the real one when
# the package is importable.
L1_DEFAULT_THRESHOLDS = {
    "battery": {"limit_ma": 200, "max_unobserved_s": 120, "max_update_age_s": 180},
    "clock": {"frequency_margin_ppm": 0.25, "h_ms": 3.7, "limit_ms": 5.0, "residual_max_ns": 1000000,
              "skew_max_ns": 1000000, "step_ns": 1000000, "t_stream_max_s": 335},
    "contention": {"cap_s": 2700, "clean_s": 600, "cpu_limit_s_per_s": 0.05, "interval_s": 30,
                   "window_interval_s": 10},
    "disk": {"headroom_bytes": 21474836480, "low_bytes": 10737418240, "planned_bytes": 22710059008},
    "instrument": {"bound_s": 55.0, "frames": 300, "max_ms_max": 200.0, "median_ms_max": 150.0},
    "thermal": {"max_gap_s": 15, "max_level": 0},
}
# Gate-prune plan section 2.3 values, as the registration is expected to seal
# them: every contract key except the two the window sizes itself.
THRESHOLDS = {
    module: {key: value for key, value in keys.items()
             if (module, key) not in (("disk", "planned_bytes"), ("clock", "t_stream_max_s"))}
    for module, keys in L1_DEFAULT_THRESHOLDS.items()
}


def threshold_defaults() -> dict[str, dict[str, Any]]:
    return json.loads(json.dumps(L1_DEFAULT_THRESHOLDS))


def stream_max_allowance() -> dict[str, Any]:
    """The committed T_stream_max allowance, verbatim (335 s)."""

    return json.loads(SIZING_ALLOWANCES.read_text())["totals"]["T_stream_max"]


def span_allowance(measurement: Path) -> dict[str, Any]:
    path = Path(measurement) / FIXTURE_SIZING_RELATIVE
    return {"seconds": FIXTURE_SIZING["totals"]["programmed_span_s"],
            "source": {"path": FIXTURE_SIZING_RELATIVE, "sha256": sha256(path)},
            "source_pointer": "/totals/programmed_span_s"}

_CALLS = '''
def record(entry):
    import json, os
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    with open(root / "calls.jsonl", "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\\n")

def behavior():
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "fake-behavior.json"
    return json.loads(path.read_text()) if path.exists() else {}
'''

FAKE_RESERVE = _CALLS + '''
import sys
record({"tool": "reserve", "argv": sys.argv[1:]})
sys.exit(int(behavior().get("reservation_rc", 0)))
'''

FAKE_FIDUCIAL = _CALLS + '''
import json, sys
from pathlib import Path
argv = sys.argv[1:]
value = lambda flag: argv[argv.index(flag) + 1]
slot = value("--slot")
record({"tool": "fiducial", "slot": slot, "argv": argv})
rc = int(behavior().get("capture_rc", {}).get(slot, 0))
if rc:
    sys.exit(rc)
directory = Path(value("--output-root")) / value("--attempt-id")
directory.mkdir(parents=True, exist_ok=False)
(directory / "instrument_evidence.json").write_text(json.dumps(
    {"b_fiducial_s": behavior().get("b_fiducial_s", 0.03), "slot": slot}))
'''

FAKE_RUN_CAMPAIGN = _CALLS + '''
import json, sys
from pathlib import Path
argv = sys.argv[1:]
value = lambda flag: argv[argv.index(flag) + 1]
if "--derive-neg8-drift-bound" in argv:
    manifest = json.loads(Path(value("--derive-neg8-drift-bound")).read_text())
    runs = Path(value("--runs-dir"))
    members = manifest["members"]
    ok = len(members) >= int(behavior().get("neg8_minimum_n", 10))
    for member in members:
        summary = runs / member["bundle_path"] / "summary_metrics.json"
        ok = ok and summary.is_file() and json.loads(summary.read_text()).get("status") == "succeeded"
    record({"tool": "derive", "members": len(members), "ok": ok, "argv": argv})
    if not ok:
        sys.exit(1)
    Path(value("--neg8-drift-bound-output")).write_text(json.dumps({"members": len(members)}))
    sys.exit(0)
config_dir, runs = Path(argv[0]), Path(value("--runs-dir"))
maximum = int(value("--max-failures"))
order = json.loads((config_dir / "order_manifest.json").read_text())["executed_order"]
fail = set(behavior().get("fail_run_ids", []))
attempted, failures = [], 0
for entry in order:
    bundle = runs / entry["run_id"]
    if (bundle / "summary_metrics.json").is_file():
        continue  # run_campaign's "skip complete"
    attempted.append(entry["run_id"])
    bundle.mkdir(parents=True)
    status = "failed" if entry["run_id"] in fail else "succeeded"
    (bundle / "summary_metrics.json").write_text(json.dumps({"status": status}))
    if status != "succeeded":
        failures += 1
    if failures >= maximum:  # run_campaign: "if failures >= args.max_failures ... break"
        break
record({"tool": "collect", "config_dir": str(config_dir), "max_failures": maximum,
        "attempted": attempted, "failures": failures})
sys.exit(1 if failures else 0)
'''

FAKE_RECOVER = _CALLS + '''
import json, sys
record({"tool": "session_status", "argv": sys.argv[1:]})
print(json.dumps({"session_state": "finalized"}))
'''


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_checkout(root: Path, *, behavior: dict[str, Any] | None = None, git: bool = True) -> Path:
    """Create a fake measurement checkout under ``root``; return its path."""

    measurement = Path(root) / "measurement"
    campaigns = measurement / "configs/campaigns"
    campaigns.mkdir(parents=True)
    for name in (*PACKS.values(), *AUXILIARY_PACKS, SIZING_PACK):
        (campaigns / name).symlink_to(REPO_ROOT / "configs/campaigns" / name)
    (measurement / FIXTURE_SIZING_RELATIVE).parent.mkdir(parents=True)
    (measurement / FIXTURE_SIZING_RELATIVE).write_text(json.dumps(FIXTURE_SIZING, indent=2) + "\n")
    (measurement / "configs/campaign_policies").mkdir()
    (measurement / "configs/campaign_policies/quiet_mac_p2_production.json").symlink_to(
        REPO_ROOT / "configs/campaign_policies/quiet_mac_p2_production.json")
    (measurement / "docs/phase_2").mkdir(parents=True)
    (measurement / "docs/phase_2/window_runbook.md").symlink_to(REPO_ROOT / "docs/phase_2/window_runbook.md")
    (measurement / "configs/calibration").mkdir()
    (measurement / "configs/calibration/calibration_ledger_head.json").write_text('{"head_digest": "fixture"}\n')
    (measurement / "runs").mkdir()
    (measurement / "runs/calibration_observation_ledger.jsonl").write_text('{"fixture": "ledger"}\n')
    (measurement / ".venv/bin").mkdir(parents=True)
    (measurement / ".venv/bin/python").symlink_to(sys.executable)
    scripts = measurement / "scripts"
    scripts.mkdir()
    for name, source in (("reserve_calibration_window_bracket.py", FAKE_RESERVE),
                         ("validate_powermetrics_fiducial.py", FAKE_FIDUCIAL),
                         ("run_campaign.py", FAKE_RUN_CAMPAIGN),
                         ("recover_calibration_ledger.py", FAKE_RECOVER)):
        (scripts / name).write_text(source)
    (measurement / "joulewise").mkdir()
    (measurement / "joulewise/__init__.py").write_text("# fake measurement package\n")
    set_behavior(measurement, behavior or {})
    if git:
        environment = dict(os.environ, GIT_AUTHOR_NAME="fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
                           GIT_COMMITTER_NAME="fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")
        for command in (["init", "-q"], ["add", "-A", "scripts", "joulewise", "configs", "docs"],
                        ["-c", "commit.gpgsign=false", "commit", "-qm", "fixture"]):
            subprocess.run(["/usr/bin/git", "-C", str(measurement), *command], check=True,
                           capture_output=True, env=environment)
    return measurement


def set_behavior(measurement: Path, behavior: dict[str, Any]) -> None:
    (Path(measurement) / "fake-behavior.json").write_text(json.dumps(behavior))


def calls(measurement: Path) -> list[dict[str, Any]]:
    path = Path(measurement) / "calls.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def inputs(root: Path, measurement: Path, pack: str, *, plan_id: str, t0_epoch_s: float,
           g10: bool = True, attempt: int = 1) -> dict[str, Any]:
    root = Path(root)
    identity = root / "identity-epoch.json"
    t1 = root / "t1-bindings.json"
    for path in (identity, t1):
        if not path.exists():
            path.write_text("{}\n")
    runs = root / "runs"
    runs.mkdir(exist_ok=True)
    return {
        "schema": "joulewise.b5_window_plan_inputs.v2", "plan_id": plan_id, "attempt": attempt,
        "pack_root": str(measurement / "configs/campaigns" / PACKS.get(pack, pack)),
        "measurement_root": str(measurement), "measurement_head": "b" * 40, "repo_head": "a" * 40,
        "custody_root": str(root / "custody"), "runs_parent": str(runs),
        "claim_backup_destination": str(root / "backup/claim"),
        "bound_backup_destination": str(root / "backup/bound"),
        "bracket_session_id": plan_id + "-calibration", "pre_attempt_id": plan_id + "-cal-pre",
        "post_attempt_id": plan_id + "-cal-post",
        "identity_epoch_json": {"path": str(identity), "sha256": sha256(identity)},
        "t1_bindings_json": {"path": str(t1), "sha256": sha256(t1)},
        "t0_epoch_s": t0_epoch_s, "programmed_span_s": span_allowance(measurement),
        "T_stream_max_s": stream_max_allowance(),
        "bytes_per_member": 190840832, "thresholds": json.loads(json.dumps(THRESHOLDS)),
        "g10": g10, "registration": None,
    }


def expected_bundles(plan: Any) -> dict[str, set[str]]:
    """Run ids every in-chain collection stage of the plan's pack should leave, per runs root."""

    window = plan.hazard_window
    tree = json.loads((Path(window["pack"]["pack_root"]) / "plan_tree.json").read_text())
    measurement = Path(plan.measurement_root)
    roots = {"claim": set(), "bound": set()}
    for row in tree["stage_graph"]:
        if row["kind"] != "campaign_collection":
            continue
        arguments = row["launch"]["commands"][0]["argv_template"]["arguments"]
        config = next(item["value"] for item in arguments if item["kind"] == "repo_path")
        root_binding = arguments[arguments.index({"kind": "literal", "value": "--runs-dir"}) + 1]["value"]
        order = json.loads((measurement / config / "order_manifest.json").read_text())["executed_order"]
        roots["bound" if root_binding == "bound_runs_root" else "claim"].update(entry["run_id"] for entry in order)
    return roots


def tree_digest(*roots: Path) -> str:
    """Digest of every path and byte under ``roots`` (absent roots count as absent)."""

    digest = hashlib.sha256()
    for root in roots:
        root = Path(root)
        digest.update(f"root {root} exists={root.exists()}\n".encode())
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            digest.update(str(path.relative_to(root)).encode() + b"\0")
            if path.is_file() and not path.is_symlink():
                digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def hazard_window_mapping(root: Path, *, pack_root: Path, g10: bool = False) -> dict[str, Any]:
    """A structurally valid hazard_window without writing a pack (for parser/installer/watchdog tests)."""

    root = Path(root)
    claim, bound = root / "runs/claim-runs", root / "runs/bound-runs"
    bindings = {
        "repo_root": str(root / "measurement"), "ledger_path": str(root / "measurement/runs/ledger.jsonl"),
        "claim_runs_root": str(claim), "bound_runs_root": str(bound),
        "operator_log_root": str(root / "custody/operator-logs"),
        "pre_calibration_dir": str(claim / "instrument_validation/pre"),
        "post_calibration_dir": str(claim / "instrument_validation/post"),
        "claim_backup_destination": str(root / "backup/claim"),
        "bound_backup_destination": str(root / "backup/bound"),
        "bracket_session_id": "fixture-calibration", "pre_attempt_id": "pre", "post_attempt_id": "post",
        "identity_epoch_json": str(root / "identity.json"), "t1_bindings_json": str(root / "t1.json"),
    }
    return {
        "schema": "joulewise.hazard_window.v1", "attempt": 1,
        "pack": {"pack_id": Path(pack_root).name, "pack_root": str(pack_root), "pack_sha256": None,
                 "plan_tree_sha256": "c" * 64, "pack_plan_id": "fixture-plan", "window_id": "fixture-window",
                 "evidence_root_id": "fixture-evidence"},
        "bracket_session_id": "fixture-calibration", "bindings": bindings,
        "runs_roots": {"claim": str(claim), "bound": str(bound)},
        "T_stream_max_s": 335, "planned_bytes": 0, "member_count": 0,
        "thresholds": json.loads(json.dumps(THRESHOLDS)), "g10": g10,
        "programmed_span_s": 600, "t0_stage_cap_s": 3300, "settle_s": 180,
        "window_env": {"path": str(root / "custody/window.env"), "sha256": "d" * 64},
        "registration": None, "chain_deviations": [], "disk_volumes": [str(claim), str(bound)],
        "stages": [{"stage_id": "fixture-reservation", "kind": "bracket_reservation", "ordinal": 1,
                    "expected_count": 1, "in_chain": True}],
    }


def hazard_plan_mapping(root: Path, *, plan_id: str, t0_epoch_s: float, window_max_s: int = 3900,
                        authored_epoch_s: float, repo_head: str = "a" * 40, measurement_head: str = "b" * 40,
                        measurement_root: Path | None = None, pack_root: Path | None = None,
                        custody_root: Path | None = None) -> dict[str, Any]:
    root = Path(root)
    custody = Path(custody_root) if custody_root is not None else root / "custody"
    pack = Path(pack_root) if pack_root is not None else REPO_ROOT / "configs/campaigns" / PACKS["alpha"]
    return {
        "schema": "joulewise.night_plan.v5", "schema_version": 5, "plan_id": plan_id,
        "receipt_class": "HAZARD_PACK", "t0_epoch_s": t0_epoch_s, "window_max_s": window_max_s,
        "authored_epoch_s": authored_epoch_s, "repo_head": repo_head,
        "measurement_root": str(measurement_root if measurement_root is not None else root / "measurement"),
        "measurement_head": measurement_head, "chain_path": str(custody / "chain.zsh"),
        "chain_sha256_path": str(custody / "chain.zsh.sha256"), "custody_root": str(custody),
        "registration_path": None, "hazard_window": hazard_window_mapping(root, pack_root=pack),
    }
