"""Compare all registered calibration loads with a scratch Git export."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]

# Evaluated in a fresh interpreter rooted at each checkout. Absolute paths
# differ between exports; registry relative paths and every loaded field must
# agree. No issued artifact, Git metadata, or evidence is written.
SNAPSHOT = """
import hashlib, json
import joulewise.calibration_bracketing as b
rows = []
for acceptance_id, row in sorted(b.ISSUED_ACCEPTANCE_REGISTRY.items()):
    loaded = b.load_calibration_acceptance_bound(row['path'])
    assert loaded is not None and b._valid_acceptance_bound(loaded), acceptance_id
    raw = row['path'].read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row['file_sha256']
    expected_build = '25G83' if acceptance_id == 'd079_calibration_acceptance_v2_n24_25g83_r2' else '25F84'
    assert loaded['identity_epoch']['os_build'] == expected_build
    rows.append({'id': acceptance_id, 'path': row['relative_path'],
                 'file_sha256': row['file_sha256'], 'loaded': loaded,
                 'generation': b._D102_GENERATION_DERIVATIONS[acceptance_id]})
historical_ids = {
    'd079_calibration_acceptance_v2_n19', 'd079_calibration_acceptance_v2_n19_r2',
    *(f'd079_calibration_acceptance_v2_n17_r{n}' for n in range(3, 9)),
}
assert set(b.ISSUED_ACCEPTANCE_REGISTRY) in (
    historical_ids, historical_ids | {'d079_calibration_acceptance_v2_n24_25g83_r2'},
)
assert not b.EPOCH_CONTINUATION_REGISTRY
assert b.load_calibration_acceptance_bound()['acceptance_id'] == b.ACTIVE_ACCEPTANCE_ID
print(json.dumps({'default': b.ACTIVE_ACCEPTANCE_ID, 'rows': rows}, sort_keys=True))
"""
def snapshot(root):
    result = subprocess.run([sys.executable, "-B", "-c", SNAPSHOT], cwd=root,
                            check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-ref", default="HEAD",
                        help="Committed predecessor tree; the uncommitted issuance is compared to it.")
    args = parser.parse_args()
    archive = subprocess.run(["git", "archive", args.reference_ref], cwd=ROOT,
                             check=True, capture_output=True).stdout
    with tempfile.TemporaryDirectory(prefix="d138-reference-export-") as tmp:
        with tarfile.open(fileobj=io.BytesIO(archive)) as source:
            source.extractall(tmp, filter="data")
        baseline = snapshot(tmp)
        current = snapshot(ROOT)
    new_id = "d079_calibration_acceptance_v2_n24_25g83_r2"
    assert baseline["default"] == "d079_calibration_acceptance_v2_n17_r8"
    assert current["default"] == new_id
    retained = [row for row in current["rows"] if row["id"] != new_id]
    assert len(baseline["rows"]) == len(retained) == 8
    assert retained == baseline["rows"], "retained registered calibration snapshot changed"
    assert len(current["rows"]) == 9
    print("REGISTERED_GENERATIONS=PASS count=9 retained=8 load_validate_identical=True default=25G83")
    digest = hashlib.sha256(json.dumps(current, sort_keys=True).encode()).hexdigest()
    print("REGISTERED_SNAPSHOT_SHA256=" + digest)


if __name__ == "__main__":
    main()
