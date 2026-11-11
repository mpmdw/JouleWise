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

from b6_r12_chain_fixture import PIN, REPO
from b6_r12_runtime import SharedClock
from b6_r12_runtime import source_root


def git_blobs(names):
    """Batch only immutable, unmeasured code/input reads, never decisions."""
    requests = [f"{PIN}:{name}" for name in names]
    raw = subprocess.run(["git", "cat-file", "--batch"], cwd=REPO,
        input=("\n".join(requests) + "\n").encode(), capture_output=True, check=True).stdout
    offset = 0
    result = {}
    for name in names:
        end = raw.index(b"\n", offset)
        header = raw[offset:end].split()
        if len(header) != 3 or header[1] != b"blob":
            raise ValueError("not a pinned source blob: " + name)
        size = int(header[2])
        offset = end + 1
        result[name] = raw[offset:offset + size]
        offset += size + 1
    if offset != len(raw):
        raise ValueError("unexpected cat-file trailing bytes")
    return result


def export_package(destination):
    names = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", PIN, "joulewise"],
                                    cwd=REPO, text=True).splitlines()
    blobs = git_blobs([name for name in names if name.endswith(".py")])
    for name, raw in blobs.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return {name: hashlib.sha256(raw).hexdigest() for name, raw in blobs.items()}


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
    (root / "b6_r12_orchestrate.py").write_bytes(Path(__file__).with_name("b6_r12_orchestrate.py").read_bytes())
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
        f"function {shlex.quote(str(root / 'input-repo/.venv/bin/python'))}() {{ {dispatch} \"$@\"; }}\n"
        'source "$1" "${@:2}"\n')
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
    for name, raw in git_blobs(selected).items():
        path = root / "pin" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        if name in modes:
            path.chmod(modes[name])
        hashes[name] = hashlib.sha256(raw).hexdigest()
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["source_sha256"].update({name: digest for name, digest in hashes.items() if name.endswith((".py", ".sh", ".zsh"))})
    manifest["pinned_input_sha256"] = {name: digest for name, digest in hashes.items() if not name.endswith((".py", ".sh", ".zsh"))}
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def init_source_repo(root):
    """A fresh synthetic code repository; no shared study checkout is opened."""
    pin = source_root(root)
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
    checkpoint = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=pin, text=True).strip()
    acceptance = pin / "configs/b6/registration/acceptance.json"
    value = json.loads(acceptance.read_text())
    value["registered_commit"] = checkpoint
    acceptance.write_text(json.dumps(value, indent=2) + "\n")
    subprocess.run(["git", "add", "configs/b6/registration/acceptance.json"], cwd=pin, check=True)
    subprocess.run(["git", "-c", "commit.gpgsign=false", "commit", "-qm", "Bind synthetic registration to its code checkpoint"], cwd=pin, check=True)
    path = root / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["synthetic_code_checkpoint"] = checkpoint
    manifest["synthetic_input_repo_head"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=pin, text=True).strip()
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def materialize_inputs(root):
    """First-write a new input repository; keep the original export unchanged."""
    pin, destination = root / "pin", root / "input-repo"
    destination.mkdir()
    overlays = json.loads((root / "input-overlays.json").read_text())
    for original in pin.rglob("*"):
        if not original.is_file():
            continue
        relative = original.relative_to(pin)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        chosen = Path(overlays.get(str(original), str(original)))
        target.write_bytes(chosen.read_bytes())
        target.chmod(original.stat().st_mode & 0o777)
    (root / "source-root.json").write_text(json.dumps({"path": str(destination)}) + "\n")
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["input_overlays"] = {str(Path(path).relative_to(pin)): hashlib.sha256(Path(target).read_bytes()).hexdigest()
                                  for path, target in overlays.items()}
    manifest["input_repository"] = str(destination)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def prepare_interpreters(root):
    """Provide the interpreter as an external environment input, never weights."""
    import shlex
    payload = "#!/bin/sh\nexec " + " ".join(map(shlex.quote, [sys.executable, "-B", str(root / "bootstrap.py"),
                                                             "--root", str(root), "dispatch"])) + ' "$@"\n'
    target = root / "interpreter/python3.13"
    target.parent.mkdir()
    target.write_text(payload)
    target.chmod(0o755)
    venv = source_root(root) / ".venv"
    (venv / "bin").mkdir(parents=True)
    (venv / "lib/python3.13/site-packages").mkdir(parents=True)
    for name in ("python", "python3", "python3.13"):
        path = venv / "bin" / name
        path.write_text(payload)
        path.chmod(0o755)


def command(root, kind, *args):
    return [sys.executable, "-B", str(root / "bootstrap.py"), "--root", str(root), kind, *map(str, args)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--bootstrap-probe", action="store_true")
    parser.add_argument("--plan-probe", choices=("alpha", "beta", "gamma"))
    parser.add_argument("--driver-probe", choices=("alpha", "beta", "gamma"))
    parser.add_argument("--loop-probe", choices=("alpha", "beta", "gamma"))
    parser.add_argument("--synthetic-models", action="store_true")
    parser.add_argument("--volume", choices=("prerequisite", "reduced", "full"), default="prerequisite")
    parser.add_argument("--denied-off", action="store_true")
    args = parser.parse_args(argv)
    root = prepare(args.out)
    (root / "source-policy.json").write_text(json.dumps({"volume": args.volume, "denied_off": args.denied_off,
        "primary_stream_duration_s": 335 if args.volume == "full" else None,
        "token_first_s": .5 if args.volume == "reduced" else 1.0,
        "token_next_s": .001 if args.volume == "reduced" else .05}, indent=2) + "\n")
    if args.bootstrap_probe:
        return subprocess.run(command(root, "probe", 60), cwd=root, check=False).returncode
    if args.plan_probe or args.driver_probe or args.loop_probe:
        export_chain_inputs(root)
        if args.synthetic_models:
            subprocess.run(command(root, "make-inputs"), cwd=root, check=True)
            materialize_inputs(root)
            prepare_interpreters(root)
        init_source_repo(root)
        if args.loop_probe:
            return subprocess.run(command(root, "loop-probe", args.loop_probe), cwd=root, check=False).returncode
        return subprocess.run(command(root, "plan", args.plan_probe or args.driver_probe,
                                      *( ["driver"] if args.driver_probe else [])), cwd=root, check=False).returncode
    parser.error("select --bootstrap-probe")


if __name__ == "__main__":
    raise SystemExit(main())
