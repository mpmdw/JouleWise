# Counts only: how many campaign manifests of a claim runs root authenticate pointwise, and whether the
# all-or-nothing catalog loads. Prints integers, booleans and fixed labels. No ids, no values.
import json, sys, os
from pathlib import Path
sys.path.insert(0, "/Users/edr/night-custody/desk/b5-harvest")
from joulewise import campaign_provenance as cp
for plan in sys.argv[1:]:
    root = Path(json.load(open("/Users/edr/night-custody/%s/night_plan.json" % plan))["hazard_window"]["runs_roots"]["claim"])
    d = root / "campaign_manifests"
    files = sorted(p for p in d.iterdir() if p.is_file()) if d.is_dir() else []
    ok = bad = bad_spare = unreadable = 0
    for f in files:
        rec = cp.load_authenticated_campaign_manifest(root, f, root / "campaign_log.jsonl")
        if rec is not None: ok += 1; continue
        bad += 1
        raw = cp.load_campaign_provenance_manifest(f)
        if raw is None: unreadable += 1
        try: bad_spare += int("spare" in f.read_text(errors="replace"))
        except OSError: pass
    cat = cp.load_authenticated_campaign_catalog(root, root / "campaign_log.jsonl")
    rows = cp.load_campaign_log_rows(root / "campaign_log.jsonl")
    att = cp.shape_valid_campaign_provenance_attestations(rows) if rows is not None else None
    print(plan, "manifest_files", len(files), "pointwise_ok", ok, "pointwise_bad", bad, "bad_unreadable", unreadable,
          "bad_mentions_spare", bad_spare, "catalog", "None" if cat is None else len(cat),
          "log_rows", "None" if rows is None else len(rows), "attestations", "None" if att is None else len(att))
