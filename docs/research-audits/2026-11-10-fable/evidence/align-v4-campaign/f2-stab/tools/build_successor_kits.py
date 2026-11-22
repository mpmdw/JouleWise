"""Regenerate the stability mint and the RL-200 stability queues."""

import argparse
import json
from pathlib import Path, PurePosixPath
import tempfile

from build_qual_pin_kits import (
    AUDIT, CAMPAIGN, QUEUE_CLI, STABILITY, build_queue, digest, git, json_bytes,
    pinned_call, pinned_source, seeded_kit,
)
INTAKE = "a2abdebdf6074dd9dd2c4ed79e332427eaecbfd0"
ROSTERS = (("f2-stab-14", range(17, 49)), ("f2-stab-16", range(49, 54)))
NOT_BEFORE = "2026-11-26"
EXPIRES = "2026-12-15T12:35:29-08:00"
INDEX = (STABILITY / "KITS.json").relative_to(AUDIT)
W2 = (CAMPAIGN / "fillers-w2").relative_to(AUDIT)
W3 = (CAMPAIGN / "fillers-w3").relative_to(AUDIT)
MULTILEG_SECTION = "\n## Multi-leg stability queues\n"


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


def multi_position_queues(week, template, positions):
    """Write one alternative per possible start and length, as in W3."""
    for size in (2, 3):
        for offset in range(len(positions) - size + 1):
            members = positions[offset:offset + size]
            first = members[0]
            legs = [leg for member in members for leg in member["legs"]]
            if len(legs) != size or any(
                member["seq"] != first["seq"] + index or len(member["legs"]) != 1
                or any(member[key] != first[key] for key in ("block_id", "kit", "not_before", "attempt"))
                for index, member in enumerate(members)
            ):
                raise ValueError(f"{first['span_id']}: expected consecutive one-leg queue positions")
            span_id = "-".join([first["block_id"], *(leg.lower() for leg in legs)])
            yield week / f"queues-{size}leg" / f"{span_id}.json", json_bytes({
                **template, "queue_id": f"cq-{span_id}",
                "spans": [{**first, "span_id": span_id, "legs": legs}],
            })


def multileg_readme(week, queues):
    command = Path(__file__).resolve().relative_to(AUDIT)
    rows = []
    for path, raw in sorted(queues.items()):
        name = path.relative_to(week).as_posix()
        rows.append(f"| [{name}]({name}) | `{digest(raw)}` |")
    return MULTILEG_SECTION + "\n".join([
        "",
        "Select the single-span queue under `queues-2leg/` or `queues-3leg/`",
        "named by the kit and all selected leg IDs in lowercase, joined by hyphens.",
        "Files give the contiguous roster alternatives. Dispatch selects only legs",
        "that are still unrun, starting at the next unrun position in kit order.",
        "Use the existing `queues-1leg/` entries for one-leg dispatch.",
        "",
        "Regenerate both weeks from the audit checkout root.",
        "",
        "```sh",
        f"python3.13 -B {command} --stability-spans",
        "```",
        "",
        "Pass `--check` to verify the multi-leg queue and README bytes.",
        "",
        "| Queue | SHA-256 |",
        "| --- | --- |",
        *rows,
        "",
    ])


def generate_stability_spans():
    """Extend the committed one-leg inventories without reminting kits."""
    artifacts = {}
    for week, kit_numbers in ((W2, range(1, 17)), (W3, range(17, 54))):
        queues = {}
        for number in kit_numbers:
            kit_id = f"f2-stab-{number:02d}"
            source = AUDIT / week / "queues-1leg"
            if week == W2:
                template = json.loads((source / f"{kit_id}.json").read_bytes())
                positions = template["spans"]
            else:
                singles = [json.loads(path.read_bytes()) for path in sorted(source.glob(f"{kit_id}-l*.json"))]
                template = singles[0]
                positions = [item["spans"][0] for item in singles]
            queues.update(multi_position_queues(week, template, positions))
        artifacts.update(queues)
        path = week / "README.md"
        base = (AUDIT / path).read_text(encoding="utf-8").partition(MULTILEG_SECTION)[0]
        artifacts[path] = (base + multileg_readme(week, queues)).encode("utf-8")
    return artifacts


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
        "A t0 of `2026-11-25T23:59:59-08:00` fails the date gate. At midnight",
        "PST the date gate passes. Dispatch still requires predecessor exhaustion",
        "and the existing rank and time-band checks.",
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
    artifacts, queues, multi = {}, {}, {}
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
                    singles = dict(single_position_queues(template, row, not_before))
                    queues.update(singles)
                    docs = [json.loads(raw) for raw in singles.values()]
                    multi.update(multi_position_queues(W3, docs[0], [doc["spans"][0] for doc in docs]))
    artifacts[INDEX] = (json.dumps(index, indent=2, sort_keys=True) + "\n").encode()
    if not_before is not None:
        artifacts.update(queues)
        artifacts.update(multi)
        artifacts[W3 / "README.md"] = readme(queues, not_before) + multileg_readme(W3, multi).encode("utf-8")
    return artifacts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--not-before", choices=(NOT_BEFORE,), help="earliest local start date")
    mode.add_argument("--kits-only", action="store_true")
    mode.add_argument("--stability-spans", action="store_true", help="regenerate W2 and W3 multi-leg queues")
    parser.add_argument("--output-root", type=Path, default=AUDIT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    artifacts = generate_stability_spans() if args.stability_spans else generate(args.not_before)
    target_index = args.output_root / INDEX
    if not args.check and INDEX in artifacts and target_index.is_file():
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
