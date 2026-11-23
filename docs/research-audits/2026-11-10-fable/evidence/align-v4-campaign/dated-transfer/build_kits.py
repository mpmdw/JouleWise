"""Build and verify the unissued RL-181 draft family at the admitted pin."""
import argparse
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime
from fnmatch import fnmatchcase
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PREFIX = HERE.relative_to(ROOT)
BASE = "eaaa1fd560cd457f4e4ccef316be62af920d08e1"
HISTORICAL = "71a83f666024c26e89cdce09dfb7a7e80d299794"
PIN = "6e9d42f1dd3d308bc9239143d0d634ab965e50e1"
QUEUE = "scripts/cadence_queue.py"
RUNNER = "scripts/cadence_legs_runner.py"
ZONE = ZoneInfo("America/Los_Angeles")
MAX_DATES = 20
MAX_LEGS = MAX_DATES * 6
T0 = datetime(2026, 11, 18, 14, tzinfo=ZONE)
DRAFT_EXPIRY = "2026-11-18T00:00:00-08:00"
DRAFT_HALT = "DRAFT: hold for effective freeze 2, registered manifest and dated lead issue"
A_TOKENS = (2000, 10000, 19458, 19458)
FULL = 4096
CYCLE = ((3724, True), (3151, False), (3724, False), (3151, True))
SEED_START = 2026111800


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


@contextmanager
def pinned_source(seat, pin=PIN):
    """Extract only versioned source into a private seat directory."""
    names = git("ls-tree", "-r", "--name-only", pin, "scripts", "joulewise").decode().splitlines()
    sources = [name for name in names if name.endswith((".py", ".sh"))]
    with tempfile.TemporaryDirectory(prefix="pinned-", dir=seat) as directory:
        with tarfile.open(fileobj=io.BytesIO(git("archive", pin, *sources))) as archive:
            archive.extractall(directory, filter="data")
        yield Path(directory)


def pinned(source, *args):
    result = subprocess.run(
        [sys.executable, "-I", "-B", *map(str, args)],
        cwd=source,
        env={**os.environ, "TMPDIR": str(source), "JW_B5_SYNTHETIC_ONLY": "1"},
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def registered_seeds():
    """Seed rosters from the public kit definitions only."""
    files = git("ls-tree", "-r", "--name-only", PIN, "docs/process/cadence/kits").decode().splitlines()
    source_paths = [(PIN, name) for name in files if name.endswith(".json")]
    patterns = (
        "item-drafts-1118/kits/cl-*.json",
        "item-drafts-rl172/kits/cl-*.json",
        "item-drafts-f2/f2-*.v1.1.json",
        "item-drafts-f2-0203/*/f2-*.v1.1.json",
        "item-drafts-f2-0203/hp-02/cl-hp-02.json",
        "f2-stab/f2-*.v1.1.json",
        "f2-stab/qual-pin/f2-*.v1.1.json",
    )
    audit_prefix = str(HERE.parent.relative_to(ROOT)) + "/"
    audit_paths = git("ls-tree", "-r", "--name-only", BASE, audit_prefix).decode().splitlines()
    source_paths.extend((BASE, name) for name in audit_paths
                        if any(fnmatchcase(name.removeprefix(audit_prefix), pattern) for pattern in patterns))
    masters, legs = set(), set()
    for revision, name in source_paths:
        kit = json.loads(git("show", f"{revision}:{name}"))
        masters.add(kit["seed_law"]["master_seed"])
        legs.update(leg["seed"] for leg in kit["legs"])
    return masters, legs


def pair_layout(kit):
    """Read the ratio from decode caps. The law's p1 label recurs for both ratios."""
    legs = kit["legs"]
    pairs = [i for i, leg in enumerate(legs) if leg["leg_type"] == "L"]
    if len(legs) != 6 or len(pairs) != 2 or kit["seed_law"]["spans"] != 1:
        raise ValueError("transfer requires one six-leg span and one L pair")
    a, b = pairs
    pair = [legs[i] for i in pairs]
    if not a or b != a + 1 or any(leg["pair"] != "p1" or leg["prefill_tokens"] != 19458 for leg in pair):
        raise ValueError("transfer's L pair must be adjacent, unsplit and after capture")
    caps = [leg["decode_tokens"] for leg in pair]
    if sorted(caps) not in ([3151, FULL], [3724, FULL]):
        raise ValueError("transfer's ratio is identified by the ruled decode caps")
    cells = sorted((leg["prefill_tokens"], leg["decode_tokens"]) for leg in legs if leg["leg_type"] == "A")
    if cells != [(prompt, FULL) for prompt in A_TOKENS]:
        raise ValueError("transfer must preserve the four qualification A cells")
    if [leg["g0_shape"] for leg in legs] != ["own"] + ["span"] * 5:
        raise ValueError("transfer requires one A capture and five consumers")
    if any(leg["start_band"] != "q0" for leg in legs):
        raise ValueError("transfer requires q0")
    return min(caps), caps[0] == FULL


def validate_layout(kits, prior_masters=(), prior_seeds=()):
    if len(kits) != MAX_DATES:
        raise ValueError("all twenty planned date places are required for the family validation")
    orders = defaultdict(set)
    layout = []
    masters, seeds = set(prior_masters), set(prior_seeds)
    for place, kit in enumerate(kits, 1):
        if kit["campaign_id"] != f"cl-transfer-{place:02}":
            raise ValueError("kit ID must match its original date place")
        cap, full_first = pair_layout(kit)
        orders[cap].add(full_first)
        layout.append((cap, full_first))
        master = kit["seed_law"]["master_seed"]
        leg_seeds = [leg["seed"] for leg in kit["legs"]]
        if master in masters or len(set(leg_seeds)) != 6 or seeds.intersection(leg_seeds):
            raise ValueError("transfer master and leg seeds must be fresh")
        masters.add(master)
        seeds.update(leg_seeds)
    if any(orders[cap] != {True, False} for cap in (3724, 3151)):
        raise ValueError("each decode ratio needs both orders over the planned roster")
    if tuple(layout) != CYCLE * (MAX_DATES // len(CYCLE)):
        raise ValueError("the ruled four-place cycle must stay in date-place order")


def make_kit(source, template, frozen, place, masters, seeds):
    cap, full_first = CYCLE[(place - 1) % len(CYCLE)]
    kit_id = f"cl-transfer-{place:02}"
    master = SEED_START
    while True:
        if master not in masters:
            generated = pinned(
                source, QUEUE, "gen-legs", "--law", "sha256-qual-v1", "--campaign-id", kit_id,
                "--master-seed", master, "--bands", "q0", "--n-legs", 6, "--spans", 1,
                "--span-a-tokens", ",".join(map(str, A_TOKENS)), "--decode-tokens", FULL,
                "--pairs", f"19458:{cap}:{FULL}", "--g0-shapes", "own,span",
            )
            pair = [leg["decode_tokens"] for leg in generated["legs"] if leg["leg_type"] == "L"]
            leg_seeds = {leg["seed"] for leg in generated["legs"]}
            if (pair[0] == FULL) == full_first and len(leg_seeds) == 6 and not seeds & leg_seeds:
                masters.add(master)
                seeds.update(leg_seeds)
                break
        master += 1
    return {**template, "frozen": frozen, **generated}


def draft_queue(kit_id, kit_ref, roster):
    return {
        "schema": "joulewise.cadence_queue.v1",
        "queue_id": f"cq-{kit_id}",
        "expires_at": DRAFT_EXPIRY,
        "halt": {"by": "draft-builder", "at": DRAFT_EXPIRY, "reason": DRAFT_HALT},
        "standing_notice": None,
        "spans": [{
            "seq": 1, "span_id": f"{kit_id}-s01", "block_id": kit_id,
            "kit": kit_ref, "legs": roster, "attempt": 1,
            "not_before": DRAFT_EXPIRY[:10],
        }],
    }


def item_text(row):
    number = row["date_place"]
    kit_id, span_id = row["kit_id"], row["span_id"]
    return f"""# DRAFT · {span_id}

**Unissued. Hold for effective freeze 2 and registered `lm-transfer-01`.** Date place {number} has no assigned date.

| Binding | Draft value |
| --- | --- |
| Kit | [{kit_id}](kits/{kit_id}.v1.1.json), SHA-256 `{row['kit']['sha256']}` |
| Queue | [cq-{kit_id}](queues/{kit_id}.queue.json), SHA-256 `{row['queue']['sha256']}` |
| Span | `{span_id}`, sequence 1, attempt 1, roster `{','.join(row['legs'])}` |
| Runner | `cadence-legs-v1.1` at `{PIN}` |
| Cells | Four A at cap 4,096. L caps in run order {row['pair_caps'][0]:,}, {row['pair_caps'][1]:,}. q0, Automatic. |
| Pinned plan | Expected {row['expected_s']:,} s, worst case {row['worst_case_s']:,} s, launch minimum {row['launch_minimum_s']:,} s. |

Use the [shared draft issue and Check](ISSUE.md). The lead fills the issue timestamp,
authenticated qualifying-window identity and record, actual America/Los_Angeles date
and both t0 bounds, committed issue-queue hash, exact predecessor and proven close.
A refusal or expired date gets a recorded disposition. There is no replacement.

```pointer
owner: magistrate
wait: none
deadline: <LEAD FILLS CHECK TARGET, ISO 8601 WITH OFFSET>
on_early_or_refused: WAIT on a higher-priority entry or a named gate within the authorized date. Record any refusal and expire an unserved date at its boundary.
next_observable: Operational Check for cq-{span_id}-a1 after proven close.
```
"""


def historical_template(place):
    path = PREFIX / "kits" / f"cl-transfer-{place:02}.v1.1.json"
    return json.loads(git("cat-file", "blob", f"{HISTORICAL}:{path}"))


def frozen_binding():
    paths = historical_template(1)["frozen"]["paths"]
    return {
        "commit": PIN,
        "paths": {path: sha256(git("cat-file", "blob", f"{PIN}:{path}")).hexdigest()
                  for path in sorted(paths)},
    }


def candidate_file(directory, relative):
    path = directory / relative
    if path.resolve() != path or not path.is_file():
        raise ValueError(f"expected a regular candidate file at {relative}")
    return path


def build_or_verify(source, directory, *, write):
    frozen = frozen_binding()
    prior_masters, prior_seeds = registered_seeds()
    masters, seeds = prior_masters.copy(), prior_seeds.copy()
    kits, rows = [], []

    def artifact(relative, data):
        path = directory / relative
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        elif candidate_file(directory, relative).read_bytes() != data:
            raise ValueError(f"{relative} differs from the reproducible candidate")
        return {"path": relative.as_posix(), "sha256": sha256(data).hexdigest()}

    for place in range(1, MAX_DATES + 1):
        kit_id = f"cl-transfer-{place:02}"
        kit_relative = PREFIX / "kits" / f"{kit_id}.v1.1.json"
        queue_relative = PREFIX / "queues" / f"{kit_id}.queue.json"
        if not write:
            kit_input = candidate_file(directory, kit_relative)
            binding = json.loads(kit_input.read_bytes())["frozen"]
            if binding["commit"] != PIN or binding["paths"].keys() != frozen["paths"].keys():
                raise ValueError(f"{kit_id} does not name the admitted pin and frozen path set")
            # Check the candidate's bytes with the admitted CLI before comparing to the rebuild.
            pinned(source, QUEUE, "validate-kit", kit_input, "--repo", ROOT)

        kit = make_kit(source, historical_template(place), frozen, place, masters, seeds)
        kits.append(kit)
        kit_ref = artifact(kit_relative, json_bytes(kit))
        roster = [leg["leg_id"] for leg in kit["legs"]]
        kit_input = directory / kit_relative
        if write:
            pinned(source, QUEUE, "validate-kit", kit_input, "--repo", ROOT)

        queue = draft_queue(kit_id, kit_ref, roster)
        if write:
            queue_ref = artifact(queue_relative, json_bytes(queue))
        queue_input = candidate_file(directory, queue_relative)
        candidate_queue = json.loads(queue_input.read_bytes())
        spans = candidate_queue["spans"]
        if len(spans) != 1 or spans[0]["kit"]["path"] != kit_ref["path"]:
            raise ValueError(f"{kit_id} queue must refer to its own candidate kit")
        pinned(source, QUEUE, "validate-queue", queue_input, "--kits-root", directory)
        decision = pinned(source, QUEUE, "next", "--queue", queue_input, "--now", T0.timestamp())
        if not candidate_queue["halt"] or decision["action"] != "halt" or decision["span_id"] is not None:
            raise ValueError(f"{kit_id} queue must halt without a span")
        if not write:
            queue_ref = artifact(queue_relative, json_bytes(queue))

        plan = pinned(source, RUNNER, "plan", "--kit", kit_input, "--t0", T0.timestamp(), "--legs", ",".join(roster))
        row = {
            "date_place": place, "kit_id": kit_id, "span_id": f"{kit_id}-s01", "kit": kit_ref, "queue": queue_ref,
            "legs": roster, "master_seed": kit["seed_law"]["master_seed"],
            "pair_caps": [leg["decode_tokens"] for leg in kit["legs"] if leg["leg_type"] == "L"],
            "expected_s": round(plan["expected_s"]), "worst_case_s": round(plan["worst_case_s"]),
            "launch_minimum_s": round(plan["launch_deadline_epoch_s"] - T0.timestamp()),
        }
        artifact(PREFIX / f"ITEM-transfer-{place:02}.md", item_text(row).encode())
        rows.append(row)

    validate_layout(kits, prior_masters, prior_seeds)
    roster = {
        "status": "draft", "issue_gate": DRAFT_HALT, "timezone": ZONE.key, "max_dates": MAX_DATES,
        "max_legs": MAX_LEGS, "runner_pin": PIN, "places": rows,
    }
    return artifact(PREFIX / "date-place-roster.json", json_bytes(roster))


def mock_span(source, directory):
    kit = candidate_file(directory, PREFIX / "kits" / "cl-transfer-01.v1.1.json")
    result = pinned(source, RUNNER, "mock", "--kit", kit, "--output", source / "synthetic-span",
                    "--t0-local", T0.replace(tzinfo=None).isoformat(), "--legs", "L001,L002,L003,L004,L005,L006")
    if result["rc"] or result["legs"] != 6 or result["stops"]:
        raise ValueError("expected a clean six-leg synthetic span")
    print("Synthetic span cl-transfer-01-s01: rc 0, six legs, zero stops.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "validate-kit", "mock"))
    parser.add_argument("--seat-dir", type=Path, required=True, help="existing private directory outside the checkout")
    parser.add_argument("--output-dir", type=Path, required=True, help="candidate root within the private seat")
    args = parser.parse_args()
    seat, output = args.seat_dir.resolve(), args.output_dir.resolve()
    if not seat.is_dir() or seat.is_relative_to(ROOT) or output.is_relative_to(ROOT):
        parser.error("the seat and candidate must be outside the checkout")
    if output == seat or not output.is_relative_to(seat):
        parser.error("the candidate must be a separate directory within the seat")
    if args.command == "build" and (output.exists() or not output.parent.is_dir()):
        parser.error("build requires a new output directory with an existing parent")
    try:
        with pinned_source(seat) as source:
            if args.command == "mock":
                mock_span(source, output)
                return
            if args.command == "build":
                with tempfile.TemporaryDirectory(prefix="candidate-", dir=seat) as staging:
                    ref = build_or_verify(source, Path(staging), write=True)
                    # Reserve the name before the atomic rename so concurrent builds cannot replace it.
                    output.mkdir()
                    try:
                        Path(staging).rename(output)
                    except OSError:
                        output.rmdir()
                        raise
            else:
                ref = build_or_verify(source, output, write=False)
    except subprocess.CalledProcessError as error:
        parser.exit(1, f"{error.stdout or ''}{error.stderr or ''}")
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"REFUSE: {error}\n")
    print(f"{MAX_DATES} kits, queues, items and plans validated. Roster SHA-256 {ref['sha256']}.")


if __name__ == "__main__":
    main()
