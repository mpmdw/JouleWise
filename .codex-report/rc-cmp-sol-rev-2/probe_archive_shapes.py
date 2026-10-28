"""Synthetic archive readiness probes; no real custody paths are opened."""
import tempfile
from pathlib import Path

from independent_recompute.support import full_pack, run_cli

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    archive = full_pack(root, "ALPHA", 5)
    rid = "fixture-decode-r01"
    raw = archive / "sources/claim-runs" / rid / "raw/powermetrics.plist"
    raw.rename(raw.with_suffix(".plist.zst"))
    rc, output, stdout = run_cli({"ALPHA": archive}, root / "recompute.json", ("--member-detail",))
    print("compressed_plist", "rc=", rc, "comparison_stopped=", output["comparison_stopped"],
          "member=", output["comparison"]["members"]["ALPHA"][rid],
          "not_compared=", output["comparison"]["summary"]["not_compared_runs"])
