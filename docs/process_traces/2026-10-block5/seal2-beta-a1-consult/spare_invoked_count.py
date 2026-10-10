# The fix seat's count (sol-fix.md, "Counts I would want"), unchanged except for the import path line.
import sys
sys.path.insert(0, "/Users/edr/night-custody/desk/b5-harvest")
from collections import Counter
from pathlib import Path
from joulewise import campaign_provenance as cp
from joulewise import whole_window as ww

try:
    root = Path(sys.argv[1])
    catalog = cp.load_authenticated_campaign_catalog(root)
    print("catalog", "authenticated" if catalog is not None else "failed",
          len(catalog or []))
    if catalog is None:
        raise SystemExit(0)

    counts = Counter()
    absent = set()
    for record in catalog:
        for member in record.value["members"]:
            slot = ww._neg8_position(member.get("role"),
                                     member.get("sentinel_position"))
            if slot not in ("start", "midpoint", "end"):
                continue
            execution = member.get("execution")
            if execution not in ("invoked", "existing", "blocked_before_invoke"):
                execution = "other"
            for bundle_id in member["bundle_ids"]:
                counts[(slot, execution)] += 1
                path = ww._safe_source_path(root, bundle_id)
                if execution == "invoked" and path is not None and not path.is_dir():
                    absent.add(bundle_id)

    for slot in ("start", "midpoint", "end"):
        for execution in ("invoked", "existing", "blocked_before_invoke", "other"):
            print("reference", slot, execution, counts[(slot, execution)])
    print("invoked_reference_absent", len(absent))

    rows = cp.load_campaign_log_rows(root / "campaign_log.jsonl")
    print("log", "readable" if rows is not None else "failed")
    exits = Counter()
    refusal_present = 0
    for row in rows or []:
        if row.get("run_id") not in absent or "exit_code" not in row:
            continue
        code = row.get("exit_code")
        bucket = "zero" if type(code) is int and code == 0 else \
                 "one" if type(code) is int and code == 1 else \
                 "two" if type(code) is int and code == 2 else "other"
        exits[bucket] += 1
        refusal_present += int(isinstance(row.get("child_refusal"), str)
                               and bool(row["child_refusal"]))
    for bucket in ("zero", "one", "two", "other"):
        print("absent_reference_log_exit", bucket, exits[bucket])
    print("absent_reference_child_refusal_recorded", refusal_present)
except Exception:
    print("scan", "failed")
    raise SystemExit(1)
