"""Build or verify the unissued RL-181 transfer kit family using the pinned cadence CLI."""
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

from date_rules import MAX_DATES, MAX_LEGS, ZONE

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
BASE = "e964c97d8278c023319b8ef748e75f0101011ca1"
PIN = "ab32a6c915a9a78f92554a89c5d0eb93333b7a39"
QUAL = HERE.parent / "item-drafts-1118" / "kits" / "cl-qual-01.v1.1.json"
QUEUE = "scripts/cadence_queue.py"
RUNNER = "scripts/cadence_legs_runner.py"
T0 = datetime(2026, 11, 18, 14, tzinfo=ZONE)
DRAFT_EXPIRY = "2026-11-18T00:00:00-08:00"
DRAFT_HALT = "DRAFT: hold for effective freeze 2, registered manifest and dated lead issue"
A_TOKENS = (2000, 10000, 19458, 19458)
FULL = 4096
CYCLE = ((3724, True), (3151, False), (3724, False), (3151, True))
SEED_START = 2026111800
TRANSFER_STOP_NOTES = (
    "RL-179 F-6 and F-9: Watcher loss raises an alarm only. A changed frozen path removes only that entry "
    "from admission. An unplanned restart has no admission effect. Keep hygiene settings fixed from "
    "freeze 2 through qual-03 close. "
    "Unproven restore or an unowned High Power marker stops all work. Retry the pinned restore once and "
    "verify the readback, then halt and page if it fails. Disk below the floor stops all work until the "
    "disk check passes. Meter absent or not polling, or collector startup failure, stops measured work "
    "until the launcher's instrument check passes. Tell the research lead. "
    "CONTAMINATED_REDOS at three in a span holds counted and v4 entries until a later span on the host "
    "closes with neither a load redo nor a load flag. A filler may probe. Apply the counted batch hold "
    "under RL-180 row 8. LEG_OVERTIME, a non-clean close, launcher refusal, desk failure or a failed "
    "consumer gate holds the affected kit or block until an input changes. Refer a consumer failure to "
    "the research lead under RL-179 F-3. The pinned runner models leg budgets and process caps."
)
INCLUSION_OVERRIDES = {
    "bands_by_history": (
        "RL-149 section 2.2 and RL-181 section 3.3: q0 begins at the leg's G0 release. "
        "The first A follows the fresh soak and supplies the span reference; the other five consume it. "
        "The pinned qualification law draws the A order and adjacent L-pair placement."
    ),
    "reserve_rule": (
        "RL-181 section 3.1: transfer uses its own 120-leg ceiling. No transfer leg is replaced. "
        "A missed opportunity spends its place and never uses the twelve-leg reserve."
    ),
    "energy_read_rule": (
        "RL-179 F-12, RL-180 and RL-181 section 3.6: frozen code reads the committed roster "
        "only at lm-transfer-01 after the terminal calendar and desks close. The desk uses only "
        "operational projections. The kit has no executable look hook."
    ),
}


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


def cli(source, *args, check=True):
    return subprocess.run(
        [sys.executable, "-B", *map(str, args)],
        cwd=source,
        env={**os.environ, "TMPDIR": str(source), "JW_B5_SYNTHETIC_ONLY": "1"},
        capture_output=True,
        text=True,
        check=check,
    )


def pinned(source, *args):
    return json.loads(cli(source, *args).stdout)


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def pinned_path(path, content):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(content).hexdigest()}


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


def make_kit(source, base, place, masters, seeds):
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
    return {
        **base,
        **generated,
        "campaign_id": kit_id,
        "title": f"DRAFT, unissued pending effective freeze 2 and lead issue. RL-181 transfer date place {place}.",
        "ruling": {"id": "RL-181", "authorizes_spans": True},
        "stop_rules": {**base["stop_rules"], "notes": TRANSFER_STOP_NOTES},
        "inclusion_rules": [
            {**row, "text": INCLUSION_OVERRIDES.get(row["id"], row["text"])}
            for row in base["inclusion_rules"]
        ],
    }


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


def build(source, write):
    base = json.loads(git("show", f"{BASE}:{QUAL.relative_to(ROOT)}"))
    if base["frozen"]["commit"] != PIN:
        raise ValueError("qualification reference differs from the unchanged runner pin")
    look_path = HERE / "looks" / "lm-transfer-01.json"
    ledger_path = HERE / "looks" / "LOOKS.json"
    look = json.loads(look_path.read_bytes())
    ledger = json.loads(ledger_path.read_bytes())
    look_entry, = [entry for entry in ledger["looks"] if entry["look_id"] == "lm-transfer-01"]
    if look["look_id"] != look_entry["look_id"] or look["status"] != "draft" or look_entry["status"] != "draft":
        raise ValueError("kit regeneration requires the unregistered transfer look and draft ledger row")
    prior_masters, prior_seeds = registered_seeds()
    masters, seeds = prior_masters.copy(), prior_seeds.copy()
    kits = [make_kit(source, base, n, masters, seeds) for n in range(1, MAX_DATES + 1)]
    validate_layout(kits, prior_masters, prior_seeds)
    validation_root = source / "draft-artifacts" if write else ROOT
    replacements = {}

    def artifact(path, data):
        if write:
            candidate = validation_root / path.relative_to(ROOT)
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate.write_bytes(data)
            replacements[path] = data
        elif path.read_bytes() != data:
            raise ValueError(f"{path.relative_to(HERE)} differs from the ruled draft")
        return pinned_path(path, data)

    rows = []
    for place, kit in enumerate(kits, 1):
        kit_id = kit["campaign_id"]
        kit_path = HERE / "kits" / f"{kit_id}.v1.1.json"
        kit_ref = artifact(kit_path, json_bytes(kit))
        roster = [leg["leg_id"] for leg in kit["legs"]]
        queue_path = HERE / "queues" / f"{kit_id}.queue.json"
        queue_ref = artifact(queue_path, json_bytes(draft_queue(kit_id, kit_ref, roster)))
        kit_input = validation_root / kit_ref["path"]
        queue_input = validation_root / queue_ref["path"]
        pinned(source, QUEUE, "validate-kit", kit_input, "--repo", ROOT)
        pinned(source, QUEUE, "validate-queue", queue_input, "--kits-root", validation_root)
        decision = pinned(source, QUEUE, "next", "--queue", queue_input, "--now", T0.timestamp())
        if decision["action"] != "halt" or decision["span_id"] is not None:
            raise ValueError(f"{kit_id} draft queue can issue")
        plan = pinned(source, RUNNER, "plan", "--kit", kit_input, "--t0", T0.timestamp(), "--legs", ",".join(roster))
        row = {
            "date_place": place, "kit_id": kit_id, "span_id": f"{kit_id}-s01", "kit": kit_ref, "queue": queue_ref,
            "legs": roster, "master_seed": kit["seed_law"]["master_seed"],
            "pair_caps": [leg["decode_tokens"] for leg in kit["legs"] if leg["leg_type"] == "L"],
            "expected_s": round(plan["expected_s"]), "worst_case_s": round(plan["worst_case_s"]),
            "launch_minimum_s": round(plan["launch_deadline_epoch_s"] - T0.timestamp()),
        }
        artifact(HERE / f"ITEM-transfer-{place:02}.md", item_text(row).encode())
        rows.append(row)

    document = {
        "status": "draft", "issue_gate": DRAFT_HALT, "timezone": ZONE.key, "max_dates": MAX_DATES,
        "max_legs": MAX_LEGS, "runner_pin": PIN, "places": rows,
    }
    ref = artifact(HERE / "date-place-roster.json", json_bytes(document))
    look["reads"]["planned_date_places"] = ref
    look["reads"]["kits"] = [{"kit_id": place["kit_id"], **place["kit"]} for place in rows]
    manifest_ref = artifact(look_path, json_bytes(look))
    look_entry["sha256"] = manifest_ref["sha256"]
    artifact(ledger_path, json_bytes(ledger))
    for path, data in replacements.items():
        path.write_bytes(data)
    print(f"{MAX_DATES} kits, queues, items and plans validated. Roster SHA-256 {ref['sha256']}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "validate-kit", "mock"))
    parser.add_argument("--seat-dir", type=Path, required=True, help="private external directory for synthetic scratch")
    args = parser.parse_args()
    with pinned_source(args.seat_dir.resolve()) as source:
        try:
            if args.command == "mock":
                kit = HERE / "kits" / "cl-transfer-01.v1.1.json"
                result = pinned(source, RUNNER, "mock", "--kit", kit, "--output", source / "synthetic-span",
                                "--t0-local", T0.replace(tzinfo=None).isoformat(),
                                "--legs", "L001,L002,L003,L004,L005,L006")
                if result["rc"] or result["legs"] != 6 or result["stops"]:
                    raise ValueError("expected a clean six-leg synthetic span")
                print("Synthetic span cl-transfer-01-s01: rc 0, six legs, zero stops.")
            else:
                build(source, write=args.command == "build")
        except subprocess.CalledProcessError as error:
            parser.exit(1, error.stdout + error.stderr)


if __name__ == "__main__":
    main()
