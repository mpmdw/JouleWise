"""Regenerate the RL-190 §1.3 stability mint and its single-position queues."""

import argparse
from datetime import date
import json
from pathlib import Path, PurePosixPath
import tempfile

from build_qual_pin_kits import (
    AUDIT, CAMPAIGN, QUEUE_CLI, STABILITY, build_queue, digest, git, json_bytes,
    pinned_call, pinned_source, seeded_kit,
)
INTAKE = "a2abdebdf6074dd9dd2c4ed79e332427eaecbfd0"
ROSTERS = (("f2-stab-14", range(17, 49)), ("f2-stab-16", range(49, 54)))
EXPIRES = "2026-12-15T12:35:29-08:00"
INDEX = (STABILITY / "KITS.json").relative_to(AUDIT)
W2 = (CAMPAIGN / "fillers-w2").relative_to(AUDIT)
W3 = (CAMPAIGN / "fillers-w3").relative_to(AUDIT)


def intake_blob(path):
    return git("show", f"{INTAKE}:{path}")


def kit_seeds(kit):
    return {kit["seed_law"]["master_seed"], *(leg["seed"] for leg in kit["legs"])}


def reserved_seeds():
    """Read only public cadence kit designs from the fixed pre-mint audit snapshot."""
    relative = CAMPAIGN.relative_to(AUDIT)
    names = git("ls-tree", "-r", "--name-only", INTAKE, str(relative)).decode().splitlines()
    reserved = set()
    for name in names:
        path = PurePosixPath(name).relative_to(relative)
        if (path.name.endswith(".v1.1.json")
                or (path.parent == PurePosixPath("item-drafts-rl172/kits") and "@" in path.name)
                or path == PurePosixPath("item-drafts-f2-0203/hp-02/cl-hp-02.json")
                or (path.parent.name.startswith(("desk-cq-", "pilot-desk-cq-"))
                    and path.name == "kit.json")):
            reserved.update(kit_seeds(json.loads(intake_blob(name))))
    return reserved


def single_position_queues(template, row, not_before):
    name = row["kit_id"]
    queue = build_queue(template, name, row["path"], row["sha256"], EXPIRES)
    for span in queue["spans"]:
        span_id = span["span_id"]
        yield W3 / "queues-1leg" / f"{span_id}.json", json_bytes({
            **queue, "queue_id": f"cq-{span_id}", "spans": [{**span, "not_before": not_before}],
        })


def readme(queues, not_before):
    command = Path(__file__).resolve().relative_to(AUDIT)
    rows = []
    for path, raw in queues.items():
        name = path.relative_to(W3).as_posix()
        rows.append(f"| [{name}]({name}) | `{digest(raw)}` |")
    return "\n".join([
        "# F2 stability successor queues",
        "",
        f"The local start boundary is `{not_before}T00:00:00-08:00`. The pinned queue schema",
        f"stores it as the local date `{not_before}`. Queues expire at `{EXPIRES}`.",
        "",
        "Pin A `2d347f721` uses kits 17–48 after kit 14. Pin B `6e9d42f1d` uses",
        "kits 49–53 after kit 16. Select the next unspent leg in kit and leg order",
        "on the eligible pin and verify the queue and kit digests. Follow the lead's",
        "successor admission item and RUN_STATE 422, 447, 463, 464 and 473.",
        "",
        "Regenerate the kits, index, queues and this README from the audit checkout root",
        "with both pinned runner commits and the intake Git object available.",
        "",
        "```sh",
        f"python3.13 -B {command} --not-before {not_before}",
        "```",
        "",
        "Pass `--check` to verify the committed bytes.",
        "",
        "| Queue | SHA-256 |",
        "| --- | --- |",
        *rows,
        "",
    ]).encode("utf-8")


def generate(not_before=None):
    index = json.loads(intake_blob(INDEX))
    old_rows = {row["kit_id"]: row for row in index["rows"]}
    reserved = reserved_seeds()
    artifacts, queues = {}, {}
    with tempfile.TemporaryDirectory(prefix="stab-successor-") as temporary:
        for predecessor, numbers in ROSTERS:
            reference = old_rows[predecessor]
            raw = intake_blob(reference["path"])
            if digest(raw) != reference["sha256"]:
                raise ValueError(f"{predecessor}: indexed digest differs from predecessor bytes")
            base = json.loads(raw)
            pin = base["frozen"]["commit"]
            if not pin.startswith(reference["runner_pin"]):
                raise ValueError(f"{predecessor}: indexed pin differs from predecessor pin")
            repo = Path(temporary) / pin
            repo.mkdir()
            pinned_source(pin, repo)
            template = json.loads(intake_blob(W2 / "queues-1leg" / f"{predecessor}.json"))
            for number in numbers:
                name = f"f2-stab-{number:02d}"
                path = INDEX.parent / "successors" / f"{name}.v1.1.json"
                kit = seeded_kit(repo, name, base, reserved)
                reserved.update(kit_seeds(kit))
                raw = artifacts[path] = json_bytes(kit)
                row = {"kit_id": name, "path": path.as_posix(),
                       "runner_pin": reference["runner_pin"], "sha256": digest(raw)}
                index["rows"].append(row)
                if not_before is not None:
                    queues.update(single_position_queues(template, row, not_before))
    artifacts[INDEX] = (json.dumps(index, indent=2, sort_keys=True) + "\n").encode()
    if not_before is not None:
        artifacts.update(queues)
        artifacts[W3 / "README.md"] = readme(queues, not_before)
    return artifacts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--not-before", type=date.fromisoformat, help="earliest local start date")
    mode.add_argument("--kits-only", action="store_true")
    parser.add_argument("--output-root", type=Path, default=AUDIT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    artifacts = generate(args.not_before.isoformat() if args.not_before else None)
    target_index = args.output_root / INDEX
    if not args.check and target_index.is_file():
        if target_index.read_bytes() not in (intake_blob(INDEX), artifacts[INDEX]):
            parser.exit(1, "KITS.json differs from both the pre-mint and regenerated index\n")
    for path, raw in artifacts.items():
        target = args.output_root / path
        if args.check:
            if not target.is_file() or target.read_bytes() != raw:
                parser.exit(1, f"regeneration differs: {path}\n")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
