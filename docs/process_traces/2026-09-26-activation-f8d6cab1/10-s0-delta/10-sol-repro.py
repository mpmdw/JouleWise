import json
import tempfile
from pathlib import Path
from joulewise import battery_float as b
from tests.test_battery_float import (
    RoundThreeAuthenticationTests, BundleAuthenticationTests, PairAuthenticationTests,
)

def result(call):
    try:
        verdict = call()
        return verdict.status
    except Exception as exc:
        return type(exc).__name__

for kind, name in (("quiet", "session.json"),
                   ("bundle", "metadata.json"),
                   ("capture", "instrument_evidence.json")):
    with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
        root = Path(tmp)
        if kind == "quiet":
            RoundThreeAuthenticationTests().quiet(root)
            call = lambda: b.authenticate_quiet_session(root)
        elif kind == "bundle":
            BundleAuthenticationTests().bundle(root)
            call = lambda: b.authenticate_bundle(root)
        else:
            pair = PairAuthenticationTests().pair(root)
            for phase in ("pre", "post"):
                pair[phase]["phase"] = "slot_" + phase
                pair[phase]["session_id"] = None
            (root / name).write_text(json.dumps({"validation_id": "v", "battery_float": pair}))
            call = lambda: b.authenticate_capture(root)
        (root / "raw/battery_float.post.ioreg").unlink()
        before = result(call)
        (root / name).write_text("{")
        after = result(call)
        print(f"{kind}: {before} -> {after}")

with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
    root = Path(tmp)
    _, pair = RoundThreeAuthenticationTests().quiet(root, rounds=True)
    hashes = {pair[phase]["raw_path"]: pair[phase]["raw_stdout_sha256"]
              for phase in ("pre", "post")}
    hashes["raw/battery_float.pre.ioreg"] = "0" * 64
    journal = root / "rounds.jsonl"
    journal.write_text(json.dumps({"raw": {"sha256": hashes}}) + "\n")
    before = result(lambda: b.authenticate_quiet_session(root))
    journal.unlink()
    after = result(lambda: b.authenticate_quiet_session(root))
    print(f"deleted rounds.jsonl: {before} -> {after}")
