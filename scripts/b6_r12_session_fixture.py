#!/usr/bin/env python3
"""R12 generator: isolated pinned programs driven by synthetic external inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from b6_r12_chain_fixture import PIN, REPO, export_package
from b6_r12_runtime import SharedClock


def prepare(root):
    """Write bootstrap inputs outside every chain-produced session subtree."""
    root = Path(root)
    lexical = root.absolute()
    if lexical.is_relative_to("/Users/edr") or "restricted" in lexical.parts:
        raise ValueError("forbidden fixture destination")
    temp = Path(tempfile.gettempdir()).resolve()
    if lexical != lexical.resolve() or not lexical.is_relative_to(temp) or lexical.exists():
        raise ValueError("fixture root must be new, resolved and below resolved TMPDIR")
    root.mkdir()
    hashes = export_package(root / "pin")
    clock = SharedClock.create(root / "clock.bin")
    clock.close()
    runtime = Path(__file__).with_name("b6_r12_runtime.py")
    (root / "runtime.py").write_bytes(runtime.read_bytes())
    (root / "arm_sources.py").write_bytes(Path(__file__).with_name("b6_r12_chain_fixture.py").read_bytes())
    (root / "bootstrap.py").write_text(
        "from runtime import bootstrap\nraise SystemExit(bootstrap())\n")
    py = str(Path(sys.executable).resolve())
    # Absolute-path shell functions substitute command *inputs* without
    # changing a byte of a rendered chain or a shell judgment.
    import shlex
    command = " ".join(map(shlex.quote, [py, "-B", str(root / "bootstrap.py"), "--root", str(root), "clock"]))
    dispatch = " ".join(map(shlex.quote, [py, "-B", str(root / "bootstrap.py"), "--root", str(root), "dispatch"]))
    (root / "shell.zsh").write_text(
        "#!/bin/zsh -f\n"
        f"function /bin/date() {{ {command} \"$@\"; }}\n"
        f"function /bin/sleep() {{ {command} sleep \"$@\"; }}\n"
        f"function {shlex.quote(str(root / 'pin/.venv/bin/python'))}() {{ {dispatch} \"$@\"; }}\n"
        'source "$1"\n')
    manifest = {"synthetic_only": True, "pin": PIN, "source_sha256": hashes,
                "generator_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
                "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "runtime_sha256": hashlib.sha256(runtime.read_bytes()).hexdigest(),
                "clock_mode": "shared integer ns; explicit sleeps advance; no wall-time scale factor",
                "volume": "bootstrap prerequisite", "seams": {
                    "time.time/time_ns/monotonic/monotonic_ns/clock_gettime_ns/sleep": "SharedClock",
                    "datetime.datetime.now/utcnow": "SharedClock wall time",
                    "zsh external /bin/date and /bin/sleep inputs": "SharedClock bootstrap CLI"}}
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return root


def export_chain_inputs(root):
    """Read only code/config Git objects, never a study tree or outcome file."""
    packs = ("d117_floor_qwen3-1p7b_v5", "d117_floor_qwen3-8b_v5", "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5",
             "neg8_reference_corpus_v5", "window_references_v5", "gamma_interior_references_v5", "window_reference_spares_v5")
    prefixes = tuple("configs/campaigns/" + pack + "/" for pack in packs) + (
        "configs/campaign_policies/", "configs/calibration/", "configs/b6/", "schemas/")
    names = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", PIN, "scripts", "configs", "schemas"],
                                    cwd=REPO, text=True).splitlines()
    # No real captures or test archives are exported, even when Git tracks one.
    selected = [name for name in names if (name.startswith("scripts/") and name.endswith((".py", ".sh", ".zsh")))
                or (name.startswith(prefixes) and name.endswith((".json", ".sha256", ".py", ".md")))]
    selected.extend(["docs/phase_2/window_runbook.md", *["configs/campaigns/v5_claim_25g83/" + name for name in
                     ("registration_block5.md", "sizing_b5.json", "flag_catalog.json", "identity_pins.json", "sealed_inventory.json")]])
    entries = subprocess.check_output(["git", "ls-tree", "-r", PIN, "scripts"], cwd=REPO, text=True).splitlines()
    modes = {entry.split("\t", 1)[1]: int(entry.split()[0], 8) & 0o777 for entry in entries}
    hashes = {}
    for name in selected:
        raw = subprocess.check_output(["git", "show", f"{PIN}:{name}"], cwd=REPO)
        path = root / "pin" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        if name in modes:
            path.chmod(modes[name])
        hashes[name] = hashlib.sha256(raw).hexdigest()
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["source_sha256"].update(hashes)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def init_source_repo(root):
    """A fresh synthetic code repository; no shared study checkout is opened."""
    pin = root / "pin"
    head = pin / "configs/calibration/calibration_ledger_head.json"
    head.write_text(json.dumps({"sequence": 0, "head_digest": "0" * 64,
                               "ledger_schema": "joulewise.calibration_observation_ledger.v1"}))
    (pin / ".gitignore").write_text("runs/\n.venv/\n__pycache__/\n*.pyc\n")
    # Disable user/system configuration before a native Git tool can open it.
    os.environ.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1", GIT_ATTR_NOSYSTEM="1",
                      GIT_AUTHOR_NAME="R12 synthetic", GIT_AUTHOR_EMAIL="r12@example.invalid",
                      GIT_COMMITTER_NAME="R12 synthetic", GIT_COMMITTER_EMAIL="r12@example.invalid",
                      GIT_AUTHOR_DATE="2026-11-11T00:00:00+00:00", GIT_COMMITTER_DATE="2026-11-11T00:00:00+00:00")
    for argv in (["init", "-q"], ["config", "core.fsmonitor", "false"], ["config", "core.attributesFile", "/dev/null"],
                 ["config", "core.hooksPath", "/dev/null"], ["add", "."],
                 ["-c", "commit.gpgsign=false", "commit", "-qm", "R12 synthetic source inputs"]):
        subprocess.run(["git", *argv], cwd=pin, check=True, capture_output=True)


def command(root, kind, *args):
    return [sys.executable, "-B", str(root / "bootstrap.py"), "--root", str(root), kind, *map(str, args)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--bootstrap-probe", action="store_true")
    parser.add_argument("--plan-probe", choices=("alpha", "beta", "gamma"))
    parser.add_argument("--driver-probe", choices=("alpha", "beta", "gamma"))
    parser.add_argument("--synthetic-models", action="store_true")
    args = parser.parse_args(argv)
    root = prepare(args.out)
    if args.bootstrap_probe:
        return subprocess.run(command(root, "probe", 60), cwd=root, check=False).returncode
    if args.plan_probe or args.driver_probe:
        export_chain_inputs(root)
        if args.synthetic_models:
            subprocess.run(command(root, "make-inputs"), cwd=root, check=True)
        init_source_repo(root)
        return subprocess.run(command(root, "plan", args.plan_probe or args.driver_probe,
                                      *( ["driver"] if args.driver_probe else [])), cwd=root, check=False).returncode
    parser.error("select --bootstrap-probe")


if __name__ == "__main__":
    raise SystemExit(main())
