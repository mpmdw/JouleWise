"""Fill the 17 RL-179 filler queues on the admitted F2 pin."""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo


CAMPAIGN = Path(__file__).resolve().parents[2]
AUDIT = CAMPAIGN.parents[4]
PIN = "2d347f721552fe03bdd19f113e7bad7a7c24908e"
WINDOWS = ("02:00-02:35", "13:14-13:15")
LA = ZoneInfo("America/Los_Angeles")


def default_expiry(now=None):
    now = datetime.now(timezone.utc) if now is None else now.astimezone(timezone.utc)
    return (now + timedelta(days=6, hours=12)).astimezone(LA).isoformat(timespec="seconds")


def offset_timestamp(value):
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if moment.utcoffset() is not None:
            return value
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("expires_at requires an ISO 8601 timestamp with an explicit offset")


def draft_paths(campaign=CAMPAIGN):
    return [
        *(campaign / "f2-stab" / "queues" / f"f2-stab-{i:02}.json" for i in range(1, 15)),
        *(campaign / "item-drafts-f2-rl179" / "queues" / f"f2-inst-{i:02}.json" for i in range(1, 4)),
    ]


def fill_queues(expires_at, campaign=CAMPAIGN):
    expires_at = offset_timestamp(expires_at)
    filled = {}
    for draft in draft_paths(campaign):
        doc = json.loads(draft.read_bytes())
        if doc["expires_at"] is not None:
            raise ValueError(f"{draft.name}: expected a draft with null expires_at")
        doc["expires_at"] = expires_at
        filled[draft.name] = (json.dumps(doc, indent=1) + "\n").encode("utf-8")

    output = campaign / "fillers-ready" / "queues"
    output.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name, raw in filled.items():
        (output / name).write_bytes(raw)
        hashes[name] = hashlib.sha256(raw).hexdigest()
    return hashes


def write_readme(expires_at, hashes):
    output = CAMPAIGN / "fillers-ready"
    script = Path(__file__).resolve().relative_to(AUDIT)
    lines = [
        "# Filled F2 queues",
        "",
        f"Runner pin `{PIN}`. Expiry **{expires_at}**.",
        f"Fast-forward by **{expires_at}** to retain an unexpired queue. See RUN_STATE.md items 422 and 425 on main.",
        "",
        "| Kit | Queue | Queue SHA-256 |",
        "| --- | --- | --- |",
        *(f"| {Path(name).stem} | [{name}](queues/{name}) | `{digest}` |" for name, digest in hashes.items()),
        "",
        "Regenerate from the audit checkout root with `PINNED_CHECKOUT` set to a clean checkout of the runner pin.",
        "",
        f'`python3.13 -I -B {script} --runner-repo "$PINNED_CHECKOUT"`',
        "",
        "[Pinned validation results by SHA-256](VERIFICATION.json)",
    ]
    (output / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(runner_repo, expires_at, hashes):
    runner_repo = runner_repo.resolve()
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=runner_repo, text=True,
    ).strip()
    if head != PIN:
        raise ValueError(f"expected runner pin {PIN}, found {head}")

    output = CAMPAIGN / "fillers-ready"
    checks = []
    for name, digest in hashes.items():
        queue = output / "queues" / name
        checks.append(("queue", digest, [
            "scripts/cadence_queue.py", "validate-queue", str(queue), "--kits-root", str(AUDIT),
        ]))
    for draft in draft_paths()[:14]:
        kit = CAMPAIGN / "f2-stab" / f"{draft.stem}.v1.1.json"
        for window in WINDOWS:
            checks.append(("stability_kit", hashlib.sha256(kit.read_bytes()).hexdigest(), [
                str(CAMPAIGN / "f2-stab" / "tools" / "validate_kit.py"), str(kit),
                "--repo", str(runner_repo), "--batch-window", window,
            ]))

    results = []
    for kind, digest, args in checks:
        completed = subprocess.run(
            [sys.executable, "-I", "-B", *args], cwd=runner_repo, capture_output=True, text=True,
        )
        argv = [
            arg.replace(str(AUDIT), "$AUDIT_CHECKOUT").replace(str(runner_repo), "$PINNED_CHECKOUT")
            for arg in args
        ]
        results.append({
            "check": kind, "sha256": digest, "argv": [Path(sys.executable).name, "-I", "-B", *argv],
            "exit_code": completed.returncode,
            "result": completed.stdout.strip() if completed.returncode else json.loads(completed.stdout),
            "stderr": completed.stderr.strip(),
        })

    evidence = {"runner_pin": head, "cwd": "$PINNED_CHECKOUT", "expires_at": expires_at, "checks": results}
    (output / "VERIFICATION.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return all(result["exit_code"] == 0 for result in results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expires-at", type=offset_timestamp, default=default_expiry())
    parser.add_argument("--runner-repo", type=Path, help="also run and record checks in this pinned checkout")
    args = parser.parse_args()
    hashes = fill_queues(args.expires_at)
    write_readme(args.expires_at, hashes)
    if args.runner_repo is not None:
        return 0 if validate(args.runner_repo, args.expires_at, hashes) else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
