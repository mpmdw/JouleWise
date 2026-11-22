"""Run frozen bundle cases independently so one failure cannot hide another."""

import argparse
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "look_path"
DRIVER = HERE / "look_path_driver.py"


def cases():
    for suite, program in (("suite", "run_suite.py"), ("suite-v2", "run_cases.py")):
        for case in json.loads((FIXTURES / suite / "cases.json").read_bytes()):
            yield suite, program, case["id"]
    suite = "suite-v3"
    vectors = json.loads((FIXTURES / suite / "vectors.json").read_bytes())
    for case in vectors["cases"]:
        yield suite, "run_cases.py", case["id"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("shard", type=int)
    parser.add_argument("total", type=int)
    args = parser.parse_args()
    if not 0 <= args.shard < args.total:
        parser.error("shard must be in [0, total)")
    status = 0
    for index, (suite, program, name) in enumerate(cases()):
        if index % args.total != args.shard:
            continue
        if name == "h_byte_identity":
            continue
        print(f"RUN {suite}/{name}", flush=True)
        result = subprocess.run([sys.executable, "-B", str(FIXTURES / suite / program),
                                 "--driver", str(DRIVER), "--case", name], check=False)
        if result.returncode:
            print(f"FAIL {suite}/{name}", flush=True)
            status = 1
    return status


if __name__ == "__main__":
    raise SystemExit(main())
