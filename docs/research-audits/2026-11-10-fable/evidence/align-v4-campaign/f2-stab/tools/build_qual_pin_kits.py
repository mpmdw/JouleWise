"""Mint and synthetically verify the two F2 stability drafts for a new pin."""

import argparse
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

STABILITY = Path(__file__).resolve().parents[1]
CAMPAIGN = STABILITY.parent
AUDIT = CAMPAIGN.parents[4]
OUTPUT = STABILITY / "qual-pin"
sys.path.insert(0, str(CAMPAIGN / "fillers-ready" / "tools"))
sys.path.insert(0, str(STABILITY / "tools"))
from fill_queues import LA, default_expiry, offset_timestamp  # noqa: E402
from validate_kit import BASE, BASE_SHA256, validate_cells  # noqa: E402


IDS = ("f2-stab-15", "f2-stab-16")
SEED_START = 2026111444
SEED_STOP = 2026211444
SYNTHETIC_T0 = "2026-11-18T12:00"
RUNNER = "scripts/cadence_legs_runner.py"
QUEUE_CLI = "scripts/cadence_queue.py"
SECTION = "\n## Qualification-pin kits\n"
HAND_READ = "../../desk-cq-dev-04-s01-a1/hand/hand_table.py"

# Run this import in a separate interpreter using only the requested pin's source.
SEED_SEARCH = """
import json
import sys

sys.path.insert(0, sys.argv[1])
from joulewise.cadence.kit_v11 import generate_legs

base = json.load(sys.stdin)
kit_id, start, stop = sys.argv[2:]
def cells(legs):
    return [{key: value for key, value in leg.items() if key != "seed"} for leg in legs]

target = cells(base["legs"])
for seed in range(int(start), int(stop)):
    law = {**base["seed_law"], "master_seed": seed}
    if cells(generate_legs(kit_id, law, base["leg_defaults"])) == target:
        print(seed)
        break
else:
    sys.exit(f"no first-hit seed in the manifest range for {kit_id}")
"""


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def json_bytes(doc):
    return (json.dumps(doc, indent=1, ensure_ascii=False) + "\n").encode("utf-8")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=AUDIT)


def pinned_source(pin, dest):
    """Extract the same source/config subset used by the qualification draft builder."""
    paths = git("ls-tree", "-r", "--name-only", pin, "scripts", "joulewise").decode().splitlines()
    paths = [path for path in paths if path.endswith((".py", ".sh"))]
    paths += ["configs/align/v4/r1_runtime.json", "configs/campaigns/align_v4/registration/inputs.json"]
    archive = git("archive", "--format=tar", pin, *paths)
    with tarfile.open(fileobj=io.BytesIO(archive)) as files:
        files.extractall(dest, filter="data")


def pinned_call(repo, *args, input_text=None):
    argv = [sys.executable, "-I", "-B", *map(str, args)]
    result = subprocess.run(argv, cwd=repo, input=input_text, text=True, capture_output=True)
    if result.returncode:
        raise ValueError(f"{args[0]} {args[1]} (exit {result.returncode}): {result.stdout}{result.stderr}".strip())
    return result.stdout


def first_seed(repo, kit_id, base):
    return int(pinned_call(repo, "-c", SEED_SEARCH, repo, kit_id, SEED_START, SEED_STOP,
                           input_text=json.dumps(base)))


def seeded_kit(repo, kit_id, base):
    seed = first_seed(repo, kit_id, base)
    law = base["seed_law"]
    generated = json.loads(pinned_call(
        repo, QUEUE_CLI, "gen-legs", "--law", law["method"], "--campaign-id", kit_id,
        "--master-seed", seed, "--n-legs", law["n_legs"], "--bands", ",".join(law["bands"]),
        "--prompt-tokens", ",".join(map(str, law["prompt_tokens"])),
        "--g0-shapes", ",".join(law["g0_shapes"]), "--decode-tokens", base["leg_defaults"]["decode_tokens"],
    ))
    kit = {
        **base, **generated, "campaign_id": kit_id, "ruling": {**base["ruling"], "id": "RL-179"},
    }
    validate_cells(kit, base)
    return kit


def build_queue(template, kit_id, kit_path, kit_sha, expires_at):
    queue = {
        **template, "queue_id": f"cq-{kit_id}", "expires_at": expires_at,
        "spans": [
            {**span, "span_id": f"{kit_id}-{span['legs'][0].lower()}", "block_id": kit_id,
             "kit": {"path": kit_path, "sha256": kit_sha}}
            for span in template["spans"]
        ],
    }
    return queue


def render_items(template, original_sha, original_pin, kit, kit_sha, plans):
    text = (template.replace("f2-stab-01", kit["campaign_id"])
            .replace(original_sha, kit_sha)
            .replace(original_pin, kit["frozen"]["commit"])
            .replace("../ISSUE.md", "../README.md#issue-template-on-this-pin"))
    blocks = text.split("\n## ")
    if len(blocks) != len(plans) + 1:
        raise ValueError("stability item template has a different number of one-leg blocks")
    for idx, plan in enumerate(plans, start=1):
        if not blocks[idx].startswith(plan["span_id"] + "\n") or "worst case 5,850 s" not in blocks[idx]:
            raise ValueError("stability item template does not match the one-leg plan")
        blocks[idx] = blocks[idx].replace("worst case 5,850 s", f"worst case {plan['worst_case_s']:,} s")
    return "\n## ".join(blocks)


def checked_kit(repo, kits_root, kit_id, base, queue_template, item_template, pin, expires_at, mock_output):
    dest = kits_root / OUTPUT.relative_to(AUDIT)
    kit_path = dest / f"{kit_id}.v1.1.json"
    queue_path = dest / "queues" / f"{kit_id}.json"
    item_path = dest / "items" / f"ITEM-{kit_id}.md"
    before = seeded_kit(repo, kit_id, base)
    kit_path.write_bytes(json_bytes(before))
    pinned_call(repo, RUNNER, "pin-kit", kit_path, "--commit", pin, "--write")
    kit_raw = kit_path.read_bytes()
    kit = json.loads(kit_raw)
    if {**kit, "frozen": before["frozen"]} != before or kit["frozen"]["commit"] != pin:
        raise ValueError(f"{kit_id}: pin-kit must change only frozen and bind the requested commit")
    if kit["frozen"]["paths"].keys() != before["frozen"]["paths"].keys():
        raise ValueError(f"{kit_id}: pin-kit changed the list of frozen paths")
    sha = digest(kit_raw)
    native_kit = json.loads(pinned_call(repo, QUEUE_CLI, "validate-kit", kit_path, "--repo", AUDIT))
    if not (native_kit["ok"] and native_kit["frozen_paths_verified"] and native_kit["kit_sha256"] == sha
            and native_kit["frozen_commit"] == pin):
        raise ValueError(f"{kit_id}: native validator did not verify the intended kit and pin")

    queue = build_queue(queue_template, kit_id, kit_path.relative_to(kits_root).as_posix(), sha, expires_at)
    queue_path.write_bytes(json_bytes(queue))
    native_queue = json.loads(pinned_call(repo, QUEUE_CLI, "validate-queue", queue_path, "--kits-root", kits_root))
    if not native_queue["ok"] or native_queue["spans"] != len(kit["legs"]):
        raise ValueError(f"{kit_id}: expected one validated queue entry for each leg")

    plans = []
    t0 = int(datetime.fromisoformat(SYNTHETIC_T0).replace(tzinfo=LA).timestamp())
    for span, leg in zip(queue["spans"], kit["legs"], strict=True):
        if span["legs"] != [leg["leg_id"]]:
            raise ValueError(f"{span['span_id']}: expected the matching seeded leg")
        plan = json.loads(pinned_call(
            repo, RUNNER, "plan", "--kit", kit_path, "--legs", leg["leg_id"], "--t0", t0,
        ))
        if plan["kit_sha256"] != sha or [row["leg_id"] for row in plan["legs"]] != span["legs"]:
            raise ValueError(f"{span['span_id']}: plan bound a different kit or roster")
        plans.append({
            "span_id": span["span_id"], "legs": span["legs"], "worst_case_s": plan["worst_case_s"],
            "launch_budget_s": int(plan["launch_deadline_epoch_s"] - plan["t0_epoch_s"]),
            "soak_retry_budget_s": plan["soak_retry_budget_s"],
        })

    leg_id = queue["spans"][0]["legs"][0]
    mock = json.loads(pinned_call(
        repo, RUNNER, "mock", "--kit", kit_path, "--legs", leg_id, "--t0-local", SYNTHETIC_T0,
        "--output", mock_output,
    ))
    mock_summary = {key: mock[key] for key in ("rc", "legs", "stops")}
    if mock_summary != {"rc": 0, "legs": 1, "stops": []}:
        raise ValueError(f"{kit_id}: synthetic mock did not close cleanly: {mock_summary}")
    item_path.write_text(render_items(item_template, queue_template["spans"][0]["kit"]["sha256"],
                                      base["frozen"]["commit"], kit, sha, plans), encoding="utf-8")
    seed = kit["seed_law"]["master_seed"]
    first_diff = next(i for i, (leg, original) in enumerate(zip(kit["legs"], base["legs"], strict=True))
                      if leg["seed"] != original["seed"])
    return {
        "kit": kit_id, "sha256": sha, "queue_sha256": digest(queue_path.read_bytes()),
        "master_seed": seed, "candidates_tested": seed - SEED_START + 1, "first_different_seed_index": first_diff,
        "positional_cells_verified": True, "only_frozen_changed_at_pin_kit": True,
        "validate_kit": native_kit, "validate_queue": native_queue,
        "plans": plans, "mock": {"leg_id": leg_id, **mock_summary},
    }


def manifest_with_rows(original, kits, pin):
    before, marker, current = original.partition(SECTION)
    if marker and "\n## " in current:
        raise ValueError("qualification-pin section must be last so other manifest sections are preserved")
    rows = [
        "",
        "Use the manifest seed procedure above and freeze the result with the named pin's own `pin-kit`.",
        "The qualification pin changes the frozen commit and path digests. The cell layout follows the same base.",
        "",
        "| Kit | SHA-256 | Runner pin | First-hit master seed | Candidates tested | First different index | Span drafts | Queue entries |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in kits:
        name = row["kit"]
        rows.append(
            f"| [{name}](qual-pin/{name}.v1.1.json) | `{row['sha256']}` | `{pin}` | "
            f"{row['master_seed']} | {row['candidates_tested']} | {row['first_different_seed_index']} | "
            f"[12 items](qual-pin/items/ITEM-{name}.md) | [12 entries](qual-pin/queues/{name}.json) |"
        )
    return before + SECTION + "\n".join(rows) + "\n"


def readme(pin, expires_at, kits):
    script = Path(__file__).resolve().relative_to(AUDIT)
    rows = []
    for kit in kits:
        name = kit["kit"]
        rows.append(
            f"| [{name}]({name}.v1.1.json) | [items](items/ITEM-{name}.md) | "
            f"[queue](queues/{name}.json) | `{kit['queue_sha256']}` |"
        )
    worst = max(plan["worst_case_s"] for kit in kits for plan in kit["plans"])
    launch = max(plan["launch_budget_s"] for kit in kits for plan in kit["plans"])
    return "\n".join([
        "# F2 stability kits for the qualification runner",
        "",
        f"Unissued product fillers for the first native run on `{pin}` (RL-179 F-11).",
        "The leg is ordinary `f2-stab` product, sealed under RL-179 row 12 and in no fit or count under RL-180 row 9.",
        f"The first run owes the F-3 (c) hand-read. [Earlier pin's hand-read template]({HAND_READ}).",
        "",
        f"Queue expiry **{expires_at}**.",
        "",
        "| Kit | One-leg drafts | Queue | Queue SHA-256 |",
        "| --- | --- | --- | --- |",
        *rows,
        "",
        "## Issue template on this pin",
        "",
        "Use the [shared issue template](../ISSUE.md) with the selected item's pin and the filled queue above.",
        "The pin's own `validate-kit --repo` verifies the staged kit. The builder records the separate RL-180 cell comparison.",
        "The pin defaults to no batch window. Its plan prints `launch_deadline_epoch_s` in place of the legacy fence field.",
        f"The synthetic plans give a work bound of {worst:,} s and a minimum launch budget of {launch:,} s including retry and cleanup.",
        "Carry the shared template's 900 s margin over the pinned minimum and use that total for the dated-block census.",
        "",
        "Regenerate from the audit checkout root with `MERGED_PIN` set to the locally available merged runner SHA.",
        "",
        f'`python3.13 -I -B {script} --pin "$MERGED_PIN"`',
        "",
        "[Synthetic verification](VERIFICATION.json)",
        "",
    ])


def build(pin, expires_at):
    pin = git("rev-parse", "--verify", "--end-of-options", f"{pin}^{{commit}}").decode().strip()
    raw_base = BASE.read_bytes()
    if digest(raw_base) != BASE_SHA256:
        raise ValueError("base f2-inst-01 SHA-256 mismatch")
    base = json.loads(raw_base)
    queue_template = json.loads((STABILITY / "queues" / "f2-stab-01.json").read_bytes())
    item_template = (STABILITY / "items" / "ITEM-f2-stab-01.md").read_text(encoding="utf-8")
    manifest = STABILITY / "MANIFEST.md"
    original_manifest = manifest.read_text(encoding="utf-8")

    OUTPUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=OUTPUT, prefix=".build-") as scratch:
        scratch = Path(scratch)
        repo = scratch / "runner"
        repo.mkdir()
        pinned_source(pin, repo)
        kits_root = scratch / "kits-root"
        dest = kits_root / OUTPUT.relative_to(AUDIT)
        (dest / "queues").mkdir(parents=True)
        (dest / "items").mkdir()
        kits = [
            checked_kit(repo, kits_root, name, base, queue_template, item_template, pin, expires_at,
                        scratch / f"{name}-mock")
            for name in IDS
        ]
        updated_manifest = manifest_with_rows(original_manifest, kits, pin)
        verification = {"pin": pin, "base_sha256": BASE_SHA256, "expires_at": expires_at,
                        "synthetic_t0_local": SYNTHETIC_T0, "kits": kits}
        (dest / "VERIFICATION.json").write_bytes(json_bytes(verification))
        (dest / "README.md").write_text(readme(pin, expires_at, kits), encoding="utf-8")
        for path in sorted(dest.rglob("*")):
            if path.is_file():
                target = OUTPUT / path.relative_to(dest)
                target.parent.mkdir(parents=True, exist_ok=True)
                path.replace(target)
        manifest.write_text(updated_manifest, encoding="utf-8")
    return verification


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pin", required=True, help="runner commit available in the local Git object store")
    parser.add_argument("--expires-at", type=offset_timestamp, default=default_expiry())
    args = parser.parse_args()
    try:
        evidence = build(args.pin, args.expires_at)
    except (ValueError, TypeError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(f"NEEDS_SPEC: {error}", file=sys.stderr)
        return 1
    for kit in evidence["kits"]:
        worst = max(plan["worst_case_s"] for plan in kit["plans"])
        print(f"{kit['kit']} {kit['sha256']} {evidence['pin']} worst case {worst:,} s mock {kit['mock']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
