#!/usr/bin/env python3
"""Read-only schema/routing validation; never writes a plan or runs a window."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.dont_write_bytecode = True
DRAFT = Path(__file__).with_name("night_plan.draft.json")
LOCAL_ZONE = ZoneInfo("America/Los_Angeles")


def instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timestamps require an explicit UTC offset")
    return parsed


def resolve_draft(draft: Path, *, t0: str, window_max_s: int, plan_id: str,
                  custody_root: str, authored_at: str) -> dict:
    """Substitute explicit inputs without publishing or claiming arm readiness."""
    value = json.loads(draft.read_text(encoding="utf-8"))
    tokens = {
        "<T0>": instant(t0).timestamp(),
        "<AUTHORED_AT>": instant(authored_at).timestamp(),
        "<WINDOW_MAX_S>": window_max_s,
        "<PLAN_ID>": plan_id,
    }
    for key, item in value.items():
        if isinstance(item, str):
            value[key] = tokens[item] if item in tokens else item.replace(
                "<NIGHT_ROOT>", custody_root
            )
    if re.search(r"<[^>]+>", json.dumps(value)):
        raise ValueError("unresolved draft placeholder")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", plan_id):
        raise ValueError("plan_id must be a single safe identity component")
    if not Path(custody_root).is_absolute() or any(ord(c) < 32 for c in custody_root):
        raise ValueError("custody root must be an absolute path without control characters")
    return value


def run(argv: list[str], *, env: dict, source: str | None = None) -> str:
    result = subprocess.run(argv, input=source, text=True, capture_output=True,
                            env=env, check=False)
    if result.returncode:
        raise ValueError(f"{argv!r} rc={result.returncode}: {result.stderr.strip()}")
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", type=Path, default=DRAFT)
    parser.add_argument("--t0", required=True, help="offset-aware ISO timestamp; <T0>")
    parser.add_argument("--window-max-s", required=True, type=int)
    parser.add_argument("--plan-id", required=True)
    parser.add_argument("--custody-root", required=True)
    parser.add_argument("--authored-at", required=True, help="offset-aware ISO timestamp")
    args = parser.parse_args()
    value = resolve_draft(args.draft, t0=args.t0, window_max_s=args.window_max_s,
                          plan_id=args.plan_id, custody_root=args.custody_root,
                          authored_at=args.authored_at)
    root = Path(value["measurement_root"])
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "GIT_OPTIONAL_LOCKS": "0",
           "PYTHONPATH": str(root)}
    head = run(["git", "-C", str(root), "rev-parse", "HEAD"], env=env)
    if head != value["measurement_head"] or head != value["repo_head"]:
        raise ValueError("clone HEAD must match both pins (driver installs from this clone)")
    sys.path.insert(0, str(root))
    from joulewise.night_gate import NightPlan, D166_REGISTRATION_SHA256
    from joulewise.night_plan_writer import night_plan_json_bytes

    plan = NightPlan.from_mapping(value)
    if plan.receipt_class != "DIAGNOSTIC_NO_PACK":
        raise ValueError("this draft is only for G2-a DIAGNOSTIC_NO_PACK")
    NightPlan.from_mapping(json.loads(night_plan_json_bytes(plan)))
    print("PASS NightPlan.from_mapping and canonical writer serialization (memory only)")
    t0 = instant(args.t0).astimezone(LOCAL_ZONE)
    if t0.second or t0.microsecond:
        raise ValueError("launchd schedule requires whole local minutes")
    deadman = t0.replace(hour=7, minute=0, second=0, microsecond=0)
    if deadman <= t0:
        deadman += timedelta(days=1)
    if t0.hour == 7 or plan.t0_epoch_s + plan.window_max_s + 300 >= deadman.timestamp():
        raise ValueError("window plus 300-second courier budget must end strictly before dead-man")
    if not 0 <= plan.t0_epoch_s - plan.authored_epoch_s <= 36 * 3600:
        raise ValueError("authorship must precede t0 by no more than 36 hours")
    registration = Path(plan.registration_path)
    if hashlib.sha256(registration.read_bytes()).hexdigest() != D166_REGISTRATION_SHA256:
        raise ValueError("D-166 registration digest mismatch")
    print(f"PASS D-166 registration sha256={D166_REGISTRATION_SHA256}")
    generator_path = root / "scripts/gen_g2_phase_d.py"
    spec = importlib.util.spec_from_file_location("g2a_clone_generator", generator_path)
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    print(run([str(root / ".venv/bin/python"), "-B", str(generator_path), "--check"], env=env))
    runsheet = generator.RUNSHEET_PATH.read_text(encoding="utf-8")
    night_date = t0.strftime("%Y%m%d")
    chain = generator.render_g2a_night_chain(runsheet, night_date)
    run(["/bin/zsh", "-n"], source=chain, env=env)
    print("PASS generated G2-a chain syntax (/bin/zsh -n, stdin; no chain file written)")
    # Execute only the actual emitted routing prefix; cut before common roots
    # and all G2-a directory creation, authentication, reservation and collection.
    boundary = "export SHAKEDOWN_ROOT="
    if chain.count(boundary) != 1:
        raise ValueError("routing boundary drift")
    routing = chain.split(boundary, 1)[0]
    print_command = '\n/usr/bin/printf "%s\\n" "$REPO" "$MEASUREMENT_HEAD" "$PY" "$PYTHONPATH"\n'
    routed = run(["/bin/zsh", "-f"], source=routing + print_command,
                 env={**env, "MEASUREMENT_ROOT": plan.measurement_root,
                      "MEASUREMENT_HEAD": plan.measurement_head,
                      "PY": "/invalid/inherited-python"}).splitlines()
    expected = [str(root), head, str(root / ".venv/bin/python"), str(root)]
    if routed != expected:
        raise ValueError(f"routing mismatch: {routed!r}")
    window_id = f"d117-g2a-prefill-probe-{night_date}"
    g2a_root = f"/Users/edr/JouleWise-shakedown-g2/g2-a-{night_date}"
    if f"export G2A_WINDOW_ID={window_id}\n" not in chain or f"export G2A_ROOT={g2a_root}\n" not in chain:
        raise ValueError("generated G2-a identity/root convention drift")
    print(f"measurement_root={routed[0]}")
    print(f"measurement_head={routed[1]}")
    print(f"interpreter={routed[2]}")
    print(run([routed[2], "-B", "--version"], env=env))
    print(f"chain={plan.chain_path} (prospective; not created)")
    print(f"chain_sha256_path={plan.chain_sha256_path} (prospective; not created)")
    print(f"chain_sha256={hashlib.sha256(chain.encode('utf-8')).hexdigest()}")
    print(f"G2A_WINDOW_ID={window_id}")
    print(f"G2A_ROOT={g2a_root}")
    print(f"t0_local={t0.isoformat()} deadman_local={deadman.isoformat()}")
    print("PASS dry validation only; magistrate inputs are not approved and no live gate was evaluated")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
