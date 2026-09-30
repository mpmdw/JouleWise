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
    assert loaded['identity_epoch']['os_build'] == '25F84'
    rows.append({'id': acceptance_id, 'path': row['relative_path'],
                 'file_sha256': row['file_sha256'], 'loaded': loaded,
                 'generation': b._D102_GENERATION_DERIVATIONS[acceptance_id]})
assert len(rows) == 7
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
    parser.add_argument("--reference-ref", default="main")
    args = parser.parse_args()
    archive = subprocess.run(["git", "archive", args.reference_ref], cwd=ROOT,
                             check=True, capture_output=True).stdout
    with tempfile.TemporaryDirectory(prefix="a341-main-export-") as tmp:
        with tarfile.open(fileobj=io.BytesIO(archive)) as source:
            source.extractall(tmp, filter="data")
        baseline = snapshot(tmp)
        current = snapshot(ROOT)
    assert baseline == current, "registered calibration snapshot changed"
    print("REGISTERED_GENERATIONS=PASS count=7 load_validate_identical=True")
    digest = hashlib.sha256(json.dumps(current, sort_keys=True).encode()).hexdigest()
    print("REGISTERED_SNAPSHOT_SHA256=" + digest)


if __name__ == "__main__":
    main()
