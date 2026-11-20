"""Read historical campaign metadata from its retained Git tree, offline."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def order_manifest(tag_path: str) -> dict:
    """Keep the original historical test oracle without current pack files."""
    try:
        blob = subprocess.run(
            ["git", "-C", str(ROOT), "show", tag_path],
            check=True, capture_output=True, timeout=10,
        ).stdout
    except subprocess.CalledProcessError as exc:
        tag = tag_path.split(":", 1)[0]
        raise AssertionError(
            f"Cannot read archived campaign {tag_path!r}; "
            f"ensure tag {tag!r} is available with git fetch --tags."
        ) from exc
    return json.loads(blob)
