#!/usr/bin/env python3
"""Compare observations from a candidate LITE adapter with the frozen decision tape."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile

import filesystem
import forms


HERE = Path(__file__).resolve().parent
CASES = json.loads((HERE / "scenarios.json").read_bytes())
NEEDS_BUILD_RESULT = {
    "drop_required_derivation_before_build", "drop_initial_ledger_before_build",
    "drop_default_policy_before_build", "unrecognized_binding_kind",
    "ordered_projection_no_ordinals", "ambient_parent_manifest", "valid_24_closure",
    "installed_frequency_helper",
}
HELPER = b"#!/bin/sh\nexit 0\n"


def integrations():
    for case in CASES:
        for spelling in case["forms"]:
            for variant in case.get("variants", ["clean"]):
                label = case["name"] + "/" + spelling
                if variant != "clean":
                    label += "/" + variant
                yield label, case["fixture"], spelling, variant


def load_adapter(path):
    spec = importlib.util.spec_from_file_location("c1_lite_candidate", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"invalid adapter path {path}")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.resolve().parent))
    spec.loader.exec_module(module)
    return module


def run_integration(adapter, work, history, fixture, spelling, variant):
    shutil.copytree(history, work / "history.git")
    calls = 0

    def edit_source(tree):
        nonlocal calls
        calls += 1
        if calls != 1:
            raise ValueError("source edit must run exactly once")
        return forms.apply(fixture, spelling, tree)

    edit = edit_source if fixture in forms.KINDS else None
    if fixture == "installed_frequency_helper":
        filesystem.put(work / "installed/frequency-helper", HELPER)
    request = {"fixture": fixture, "form": spelling, "variant": variant,
               "report_build": edit is not None or fixture in NEEDS_BUILD_RESULT}
    result = adapter.exercise(work, request, edit)
    if edit and calls != 1:
        raise ValueError("adapter skipped the frozen source edit")
    if fixture == "installed_frequency_helper":
        # Compare the actual arm-record path while keeping per-run temp names off the tape.
        external = result["external"]
        path = Path(external["path"])
        result = {**result, "external": {**external, "path": path.relative_to(work).as_posix()}}
    return result


def check_labels(tape, labels):
    rows = [json.loads(line) for line in tape.splitlines()]
    if len(set(labels)) != len(labels) or [row["case"] for row in rows] != labels:
        raise ValueError("case names or order differ from the freeze")
    if b"".join(filesystem.encode(row) for row in rows) != tape:
        raise ValueError("noncanonical decision tape")


def verify(actual, tape):
    observed = b"".join(actual)
    if observed != tape:
        for number, (got, want) in enumerate(zip(actual, tape.splitlines(keepends=True)), 1):
            if got != want:
                raise ValueError(f"decision {number} differs\nobserved {got!r}\nexpected {want!r}")
        raise ValueError("decision tape lengths differ")
    sys.stdout.buffer.write(observed)


def record(actual, label, observation):
    if not isinstance(observation, dict) or "case" in observation:
        raise ValueError(f"{label}: adapter must return observation fields only")
    actual.append(filesystem.encode({"case": label, **observation}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    route = parser.add_mutually_exclusive_group(required=True)
    route.add_argument("--adapter", type=Path)
    route.add_argument("--fixture-check", action="store_true")
    args = parser.parse_args()
    adapter = load_adapter(args.adapter) if args.adapter else None
    tape = (HERE / "expected.jsonl").read_bytes()
    walks = list(filesystem.vectors())
    runs = list(integrations())
    labels = [family + "/" + op for family, op in walks] + [row[0] for row in runs]
    check_labels(tape, labels)
    actual = []
    with tempfile.TemporaryDirectory(prefix="c1-lite-") as name:
        tmp = Path(name).resolve()
        seed = tmp / "seed"
        authority = filesystem.seed(seed)
        history = tmp / "history.git"
        filesystem.history(HERE, history)
        for family, op in walks:
            with tempfile.TemporaryDirectory(dir=tmp) as base:
                request = filesystem.view(seed, Path(base), authority, family, op)
                if adapter:
                    record(actual, family + "/" + op, adapter.check_view(request))
        if adapter:
            for label, fixture, spelling, variant in runs:
                with tempfile.TemporaryDirectory(dir=tmp) as base:
                    try:
                        result = run_integration(adapter, Path(base), history, fixture, spelling, variant)
                        record(actual, label, result)
                    except Exception as exc:
                        raise RuntimeError(f"adapter failed in {label}") from exc
            verify(actual, tape)
        else:
            print(f"Constructed {len(walks)} filesystem fixtures and verified history. "
                  f"Checked {len(runs)} integration row names. Candidate untested.")


if __name__ == "__main__":
    main()
