"""Read historical campaign metadata from its retained Git tree, offline."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def order_manifest(tag_path: str) -> dict:
    """Keep the original historical test oracle without current pack files."""
    blob = subprocess.run(
        ["git", "-C", str(ROOT), "show", tag_path],
        check=True, capture_output=True,
    ).stdout
    return json.loads(blob)
