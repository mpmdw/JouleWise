"""Render or execute the throwaway launchd OSCTX cell sequence."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import threading
import time

try:
    from .common import cell_name, cells, load_config, write_json
    from .cell import hid_idle_seconds
except ImportError:  # direct CLI execution
    from common import cell_name, cells, load_config, write_json
    from cell import hid_idle_seconds


def label(state: str, context: str, number: int) -> str:
    return f"com.joulewise.dummy.osctx.{state}.{context}.{number}"


def plist_for(state: str, context: str, number: int, cell_dir: Path, config_path: Path, config: dict, python: str) -> dict:
    result = {
        "Label": label(state, context, number),
        "ProgramArguments": [python, str(Path(__file__).with_name("cell.py")), "--out", str(cell_dir),
                             "--state", state, "--context", context, "--cell-id", str(number), "--config", str(config_path)],
        "EnvironmentVariables": {"HF_HUB_OFFLINE": "1", "HOME": os.environ["HOME"]},
        "StandardOutPath": str(cell_dir / "stdout.log"),
        "StandardErrorPath": str(cell_dir / "stderr.log"),
        "RunAtLoad": True,
    }
    process_type = config["contexts"][context]
    if process_type is not None:
        result["ProcessType"] = process_type
    return result


def plan(out: Path, config_path: Path, config: dict, states: list[str], python: str) -> list[dict]:
    out.mkdir(parents=True, exist_ok=True)
    uid = os.getuid()
    actions = []
    for state, context, number in cells(config, states):
        directory = (out / cell_name(state, context, number)).resolve()
        directory.mkdir(parents=True, exist_ok=True)
        plist_path = directory / "job.plist"
        with plist_path.open("wb") as stream:
            plistlib.dump(plist_for(state, context, number, directory, config_path, config, python), stream)
        actions.append({"state": state, "context": context, "cell_id": number, "cell_dir": str(directory),
                        "label": label(state, context, number), "plist": str(plist_path),
                        "commands": [["/bin/launchctl", "bootstrap", f"gui/{uid}", str(plist_path)],
                                     ["/bin/launchctl", "bootout", f"gui/{uid}", str(plist_path)],
                                     ["/usr/bin/pgrep", "-f", label(state, context, number)],
                                     ["/usr/bin/pgrep", "-f", str(directory / "powermetrics.plist")]]})
    sequence = [{"continuous_census": ["/usr/bin/top", "-l", "1", "-o", "cpu", "-n", "15", "-stats", "pid,command,cpu,time"],
                 "interval_seconds": config["census_interval_seconds"]}]
    for index, action in enumerate(actions):
        if action["state"] == "U":
            sequence.append({"gate": "HIDIdleTime", "minimum_seconds": config["hid_idle_seconds"], "poll_seconds": config["hid_poll_seconds"]})
        if action["state"] == "S":
            sequence.append(["/usr/bin/pmset", "displaysleepnow"])
        sequence.extend(action["commands"])
        if action["state"] == "S" and (index + 1 == len(actions) or actions[index + 1]["state"] != "S"):
            sequence.append(["/usr/bin/caffeinate", "-u", "-t", "1"])
    write_json(out / "command_sequence.json", {"states": states, "actions": actions, "sequence": sequence,
        "state_U": f"wait HIDIdleTime >= {config['hid_idle_seconds']} s before each cell",
        "state_S_before_each": ["/usr/bin/pmset", "displaysleepnow"],
        "state_S_after": ["/usr/bin/caffeinate", "-u", "-t", "1"],
        "census": ["/usr/bin/top", "-l", "1", "-o", "cpu", "-n", "15", "-stats", "pid,command,cpu,time"]})
    with (out / "events.jsonl").open("a") as stream:
        stream.write(json.dumps({"event": "render", "wall_ns": time.time_ns(), "states": states, "cells": len(actions)}) + "\n")
    return actions


def wait_for_idle(threshold: float, poll: float, read=hid_idle_seconds, sleep=time.sleep, log=lambda **_: None) -> None:
    paused = False
    while True:
        idle = read()
        log(event="hid_check", idle_seconds=idle)
        if idle >= threshold:
            if paused:
                log(event="hid_pause_end", idle_seconds=idle)
            return
        if not paused:
            log(event="hid_pause_start", idle_seconds=idle)
            paused = True
        sleep(poll)


def run_command(argv: list[str], log) -> subprocess.CompletedProcess:
    log(event="command", argv=argv)
    result = subprocess.run(argv, capture_output=True, text=True, check=False)
    log(event="command_result", argv=argv, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
    return result


def census_loop(path: Path, stop: threading.Event, interval: float, log) -> None:
    while not stop.is_set():
        argv = ["/usr/bin/top", "-l", "1", "-o", "cpu", "-n", "15", "-stats", "pid,command,cpu,time"]
        result = subprocess.run(argv, capture_output=True, text=True, check=False)
        record = {"wall_ns": time.time_ns(), "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
        with path.open("a") as stream:
            stream.write(json.dumps(record) + "\n")
        log(event="census", returncode=result.returncode)
        stop.wait(interval)


def execute(out: Path, actions: list[dict], config: dict) -> None:
    lock = threading.Lock()
    def log(**values):
        with lock, (out / "events.jsonl").open("a") as stream:
            stream.write(json.dumps({"wall_ns": time.time_ns(), "mono_ns": time.monotonic_ns(), **values}) + "\n")
    stop = threading.Event()
    census = threading.Thread(target=census_loop, args=(out / "census.jsonl", stop, config["census_interval_seconds"], log), daemon=True)
    census.start()
    log(event="runner_start", cells=len(actions))
    active_state = None
    try:
        for action in actions:
            state = action["state"]
            if state != active_state:
                if active_state == "S":
                    result = run_command(["/usr/bin/caffeinate", "-u", "-t", "1"], log)
                    if result.returncode:
                        raise RuntimeError("display wake failed")
                active_state = state
                log(event="state_start", state=state)
            if state == "U":
                wait_for_idle(config["hid_idle_seconds"], config["hid_poll_seconds"], log=log)
            if state == "S":
                result = run_command(["/usr/bin/pmset", "displaysleepnow"], log)
                if result.returncode:
                    raise RuntimeError("display sleep failed")
            directory = Path(action["cell_dir"])
            if (directory / "done.json").exists():
                raise FileExistsError(f"cell already has a done marker: {directory}")
            booted = False
            try:
                result = run_command(action["commands"][0], log)
                if result.returncode:
                    raise RuntimeError(f"bootstrap failed: {action['label']}")
                booted = True
                deadline = time.monotonic() + config["timeout_seconds"]
                while not (directory / "done.json").exists():
                    if time.monotonic() >= deadline:
                        raise TimeoutError(f"cell timed out: {action['label']}")
                    time.sleep(.5)
                done = json.loads((directory / "done.json").read_text())
                log(event="cell_done", label=action["label"], done=done)
                if not done["ok"]:
                    raise RuntimeError(f"cell failed: {action['label']}")
            finally:
                if booted:
                    result = run_command(action["commands"][1], log)
                    if result.returncode:
                        log(event="bootout_failure", label=action["label"])
                for argv in action["commands"][2:]:
                    survivor = run_command(argv, log)
                    if survivor.returncode == 0:
                        raise RuntimeError(f"survivor after bootout: {argv}")
                    if survivor.returncode != 1:
                        raise RuntimeError(f"pgrep failed: {argv}")
        log(event="runner_done")
    finally:
        if active_state == "S":
            result = run_command(["/usr/bin/caffeinate", "-u", "-t", "1"], log)
            if result.returncode:
                log(event="display_wake_failure", returncode=result.returncode)
        stop.set()
        census.join(timeout=10)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--render-only", type=Path)
    mode.add_argument("--out", type=Path)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("config.json"))
    parser.add_argument("--state", action="append")
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    out = (args.render_only or args.out).resolve()
    actions = plan(out, args.config.resolve(), config, args.state or config["states"], args.python)
    if args.out:
        execute(out, actions, config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
