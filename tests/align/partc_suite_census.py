"""The frozen differential suite, run byte for byte, with the census frozen ``Segment.run`` writes on every member.

Lead fix round r2 of 2026-11-22, R3 and its LEAD GATE. Suite v3.1's synthetic clean fixture has no closing census
on the soak and no census on D_bank or X_G, so under R3 its clean control refuses. The lead is issuing v3.2: v3.1
plus a complete-census clean fixture, with expectations otherwise unchanged. Until it is adopted, this runs the
suite file at its repo path unmodified, with only the clean control's member close wrapped by
``partc_audit_probe.census_stand_in``. That adds the missing census points (both points; for the soak, the closing
one) and nothing else. On a fixture that already carries both points it adds nothing, and the run is the suite's
own. It ends by printing how many points it added and the suite file's digest.

    python3.13 -IB tests/align/partc_suite_census.py      (the suite's own JW_PARTC_* variables apply)
"""
import hashlib
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUITE = HERE / "test_partc_frozen_differential.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main():
    suite = load("partc_frozen_suite", SUITE)
    probe = load("partc_probe", HERE / "partc_audit_probe.py")
    issued_control = suite.control

    def control(directory):
        with probe.census_stand_in(suite):
            return issued_control(directory)

    suite.control = control
    try:
        suite.main()
    finally:
        print("suite sha256", hashlib.sha256(SUITE.read_bytes()).hexdigest(), "census stand-in points added",
              len(probe.ADDED), sorted(set(probe.ADDED)), flush=True)


if __name__ == "__main__":
    main()
