import sys, json, tempfile, hashlib, shutil
sys.path.insert(0, "/Users/edr/code/JouleWise-wt-s1-step2-d528efb2")
from pathlib import Path
from tests.bfgs_fixtures import produce_strict_bundle
from joulewise.bundle_read import authenticate_window_members, BundleReader
from joulewise.whole_window import custody_telemetry_identity
from joulewise.cli import validate_bundle

def rebind(b, mutate):
    c = json.loads((b/"config.json").read_text()); mutate(c)
    (b/"config.json").write_text(json.dumps(c)+"\n")
    md = json.loads((b/"metadata.json").read_text()); md["config_sha256"] = hashlib.sha256((b/"config.json").read_bytes()).hexdigest()
    (b/"metadata.json").write_text(json.dumps(md)+"\n")

def setmock(c): c["hardware_target"]["telemetry_backend"] = "mock"

with tempfile.TemporaryDirectory(dir="/tmp/cg-s1route-d528efb2") as tmp:
    root = Path(tmp)
    base = produce_strict_bundle(root, "base")
    cases = {}
    for name in ("control", "config_deleted", "config_rebound_mock", "config_byte_changed_unbound", "config_mock_unbound", "config_not_json"):
        p = root / name
        shutil.copytree(base, p)
        cases[name] = p
    (cases["config_deleted"]/"config.json").unlink()
    rebind(cases["config_rebound_mock"], setmock)
    raw = (cases["config_byte_changed_unbound"]/"config.json").read_bytes()
    (cases["config_byte_changed_unbound"]/"config.json").write_bytes(raw + b" ")
    c = json.loads((cases["config_mock_unbound"]/"config.json").read_text()); setmock(c)
    (cases["config_mock_unbound"]/"config.json").write_text(json.dumps(c)+"\n")
    (cases["config_not_json"]/"config.json").write_bytes(b"not json")
    for n, p in cases.items():
        row = {}
        try:
            v = authenticate_window_members([(n, p)])
            row["gate"] = {k: x.status for k, x in v.items()}
        except Exception as e:
            row["gate"] = f"RAISED {type(e).__name__}: {str(e)[:160]}"
        try:
            r = BundleReader(p); r.metadata(); row["reader.metadata"] = r.battery_float_status
        except Exception as e:
            row["reader.metadata"] = f"RAISED {type(e).__name__}: {str(e)[:160]}"
        try:
            i = custody_telemetry_identity(p)
            row["identity"] = dict(bound=i.custody_bound_config, mock=i.mock_config, exempt=i.production_predicate_exempt, triangle=i.triangle_agrees)
        except Exception as e:
            row["identity"] = f"RAISED {type(e).__name__}: {str(e)[:160]}"
        try:
            row["strict"] = validate_bundle(p, strict=True)
        except Exception as e:
            row["strict"] = f"RAISED {type(e).__name__}: {str(e)[:160]}"
        print("==", n)
        for k, val in row.items(): print("    ", k, "->", val)
