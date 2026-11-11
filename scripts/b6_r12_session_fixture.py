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

os.environ.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1", GIT_ATTR_NOSYSTEM="1",
                  PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1",
                  PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin")
os.environ["XDG_CONFIG_HOME"] = str(Path(tempfile.gettempdir()).resolve() / "r12-xdg-empty")

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
                "orchestrator_sha256": hashlib.sha256((root / "b6_r12_orchestrate.py").read_bytes()).hexdigest(),
                "arm_sources_sha256": hashlib.sha256((root / "arm_sources.py").read_bytes()).hexdigest(),
                "generator_files_sha256": {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                    for name in ("b6_r12_session_fixture.py", "b6_r12_runtime.py", "b6_r12_orchestrate.py", "b6_r12_verify.py", "b6_r12_chain_fixture.py")},
                "clock_mode": "shared integer ns; explicit sleeps advance; no wall-time scale factor",
                "volume": "bootstrap prerequisite", "seams": {
                    "time.time/time_ns/monotonic/monotonic_ns/clock_gettime_ns/sleep": "SharedClock",
                    "time.CLOCK_UPTIME_RAW input": "same no-sleep ns frontier as CLOCK_MONOTONIC_RAW; original sleep-offset reader and flags run",
                    "datetime.datetime.now/utcnow": "SharedClock wall time",
                    "subprocess._time / threading._time": "same shared monotonic clock, including stdlib aliases",
                    "SharedClock notification transport": "only registered receivers poll stop inputs, nominal 10 ms real poll interval (OS scheduling may delay it); shared ns always reread under lock, never cached",
                    "zsh external /bin/date and /bin/sleep inputs": "SharedClock bootstrap CLI"}}
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return root


def declare_sources(root):
    """Record source substitutions and policies before chain execution."""
    path = root / "manifest.json"
    value = json.loads(path.read_text())
    value["seams"].update({
        "joulewise.hazards.arm.run.__defaults__[0]": "real Seams object: synthetic Context.run/clocks, frequency_reader, disk stat/statvfs, host_cpu; no arm/run/judge replacement",
        "joulewise.b5.driver.Seams.__init__.__defaults__": "Popen source dispatcher; disk_free = 1 TiB",
        "joulewise.b6.sleep_guard.KeepAwake.__init__.__defaults__": "declared caffeinate and pmset command results; no host action",
        "joulewise.hazards.monitor.Monitor.__init__.__kwdefaults__": "Context, zero frequency, 4 TiB available disk and idle host CPU counters",
        "joulewise.hazards.thermal.NotifyReader": "OS thermal level 0 external reader",
        "joulewise.hazards.battery.RegistryReader": "fresh AC-connected, not-charging battery; 0 mA, 12000 mV",
        "joulewise.hazards.smc.Reader": "external SMC reader: declared keys 0; no native SMC call",
        "joulewise.external.km003c_usb.load_libusb": "library object returns protocol bytes; unchanged UsbDevice/Meter/writer; 20 V, 10 W baseline + engine activity, 50 Hz",
        "subprocess.Popen._execute_child": "dispatch unchanged pinned children; sampler raw plists at 10 Hz; first-source-tick startup barrier; undeclared commands return 126 and are logged",
        "mlx.core / mlx_lm": "tiny engine library source, batch 1; matmul pulse source 50 W; request first/decode 10/6 W; token/model timings in source policy; original runtime, events and reducers run; weights never loaded",
        "Tokenizer.encode/decode": "original input token IDs and 1 ms source latency",
        "mlx_lm.load source argument / raw sampler script": "model-source-PID.json outside session trees; scripted science-only busy readings keyed by the public engine input, references kept clean; no controller internals inspected",
        "joulewise.adapters.powermetrics.PowermetricsTelemetryAdapter.__init__.__kwdefaults__.drain_sleep": "minimum 200 ms external scheduler quantum; original right-edge drain judgment",
        "calibration CLI clock entry phase": "next whole monotonic second + 132 ns; original pulse protocol/detection/refit",
        "builtins.open/io.open/os.stat/os.lstat on /usr/bin/powermetrics": "declared synthetic executable identity bytes, hashed by original code",
        "sys._base_executable for venv": "fixture interpreter bootstrap script; original stdlib venv and pinned smoke wrapper writers run",
        "tempfile.tempdir / os.devnull": str(root / "tmp") + " / " + str(root / "null-sink"),
        "JOULEWISE_CUSTODY_PARENT": str(root / "host-state"),
        "joulewise.b6.driver_lane.DriverLane.group_alive": "declared absent after the directly scheduled driver returned",
        "joulewise.b6.precheck.Seams.orphan_collect": "declared empty external process observation",
        "Loop.clock / DriverLane.clock": "shared injected wall clock; original transitions, status and attempt writers",
        "scheduler": "call actual run_night at plan t0; installer/uninstaller command results 0; no launchd job",
        "JOULEWISE_WHOLE_WINDOW_WORKERS": "1; pinned environment concurrency input; unchanged strict validator in its isolated verdict process, no spawned interpreter outside bootstrap",
        "os.kill/os.killpg and joulewise.b5.harvest.Seams.killpg": "only owned live child SIGTERM has declared success; no native signal executes; per-PID external signal input reaches the original registered meter/monitor handler; other actions denied and logged",
        "os.killpg(pgid, 0)": "declared external group census: live owned Popen is present, otherwise ESRCH (not EPERM); original harvest readiness and teardown judge it",
        "zsh file utilities": "unchanged rendered program uses cat/mkdir/jq on its fixture-bound paths; date/sleep source functions and bootstrap interpreter isolate time and host commands",
        "Git, /bin/cp -c -pR and zstd": "actual fixture-scoped code/input Git, non-symlink fixture-only APFS copy writer and desk codec; no network Git; no simulated copying or compression"})
    value["seams"]["subprocess.run / ChainSources.subprocess_run Git blob input"] = (
        "only captured git -C <fixture-repo> cat-file blob <full SHA-1>; actual Git --batch transport reads each request; "
        "no blob/ref/result/decision cache; mutable commands and anomalous/type/hash responses use the original invocation; "
        "private input repositories have no replace refs, and attempts to create them are denied")
    value["actions"] = {"default": "deny rc 126, stdout empty, stderr RL-49 default deny; execute nothing",
        "network_time_off": "normal success rc 0; extra denied fixture uses 126",
        "display_sleep": "success rc 0, empty stdout/stderr, execute nothing",
        "installer_and_uninstaller": "success rc 0, declared diagnostic stdout, execute nothing",
        "caffeinate": "declared live handle; pmset assertions source confirms it; execute nothing",
        "results": "complete argv/rc/stdout/stderr/executed=false receipts in source-calls-*.jsonl"}
    value["redirections"] = {"host-state": str(root / "host-state"), "temp": str(root / "tmp"),
                              "devnull": str(root / "null-sink"), "escaping_writes": "denied",
                              "XDG_CONFIG_HOME": str(root / "host-state/xdg"),
                              "Git global/system configuration": "/dev/null; system disabled; no per-user defaults followed"}
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


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
    if pin == root / "pin":
        raise ValueError("original pinned export is read-only; materialize synthetic inputs first")
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
    parser.add_argument("--nine-session-set", action="store_true")
    parser.add_argument("--seed-probe", action="store_true")
    parser.add_argument("--synthetic-models", action="store_true")
    parser.add_argument("--volume", choices=("prerequisite", "reduced", "full"), default="prerequisite")
    parser.add_argument("--denied-off", action="store_true")
    parser.add_argument("--deny-normal-session", action="store_true",
                        help="deny OFF only in the ordinary session; keep prerequisite/smoke actions normal")
    args = parser.parse_args(argv)
    root = prepare(args.out)
    (root / "source-policy.json").write_text(json.dumps({"volume": args.volume, "denied_off": args.denied_off or args.deny_normal_session,
        "denied_normal": args.deny_normal_session,
        "primary_stream_duration_s": 335 if args.volume == "full" else 65,
        "token_first_s": .5 if args.volume == "reduced" else 1.0,
        "token_next_s": .001 if args.volume == "reduced" else .05}, indent=2) + "\n")
    if args.bootstrap_probe:
        return subprocess.run(command(root, "probe", 60), cwd=root, check=False).returncode
    if args.plan_probe or args.driver_probe or args.loop_probe or args.nine_session_set or args.seed_probe:
        if not args.synthetic_models:
            parser.error("chain programs require --synthetic-models and a separate input repository")
        export_chain_inputs(root)
        if args.synthetic_models:
            subprocess.run(command(root, "make-inputs"), cwd=root, check=True)
            materialize_inputs(root)
            prepare_interpreters(root)
        init_source_repo(root)
        declare_sources(root)
        if args.seed_probe:
            return subprocess.run(command(root, "seed-probe"), cwd=root, check=False).returncode
        if args.nine_session_set:
            with (root / "generator.stdout").open("wb") as out, (root / "generator.stderr").open("wb") as err:
                return subprocess.run(command(root, "loop-probe", "all", "9"), cwd=root,
                                      stdout=out, stderr=err, check=False).returncode
        if args.loop_probe:
            return subprocess.run(command(root, "loop-probe", args.loop_probe), cwd=root, check=False).returncode
        return subprocess.run(command(root, "plan", args.plan_probe or args.driver_probe,
                                      *( ["driver"] if args.driver_probe else [])), cwd=root, check=False).returncode
    parser.error("select --bootstrap-probe")


if __name__ == "__main__":
    raise SystemExit(main())
