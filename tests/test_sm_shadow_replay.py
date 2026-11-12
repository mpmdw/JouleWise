"""Targeted tests for scripts/sm_shadow_replay.py on small synthetic night trees."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location(
    "sm_shadow_replay", Path(__file__).resolve().parents[1] / "scripts" / "sm_shadow_replay.py")
replay = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(replay)

NOW = 2_000_000_000.0
GOOD_COURIER = {"sent": True, "exit_code": 0}


def write(root: Path, name: str, files: dict):
    d = root / name
    d.mkdir(parents=True)
    for fname, content in files.items():
        p = d / fname
        if isinstance(content, (dict, list)):
            p.write_text(json.dumps(content))
        else:
            p.write_text(content or "")
    return d


def go_night(exit_code=0, **extra):
    files = {
        "result.json": {"verdict": "GO", "chain_exit_code": exit_code},
        "chain.started": {"pid": 1}, "chain.exited": {"exit_code": exit_code},
        "hazard_result.json": {"verdict": "GO", "chain": {"exit_code": exit_code}, "faults": {"reasons": []}},
        "courier.json": GOOD_COURIER, "courier.sent": "",
    }
    files.update(extra)
    return files


def run(tmp_path, name, files):
    _, loaded = replay.load_tree_night(write(tmp_path, name, files))
    return replay.replay_night(name, loaded, NOW)


def ids(night, status="disagree"):
    return {c["id"] for c in night["agreement"]["checks"] if c["status"] == status}


def test_agree_case_has_no_disagreement_except_legacy_courier_gap(tmp_path):
    n = run(tmp_path, "b5-ok", go_night())
    assert n["shadow"]["outcome"] == "MEASURED_OK"
    assert n["shadow"]["state"] == "Delivered"
    assert ids(n) <= {"invariant:COURIER_SENT_WITHOUT_DELIVERY"}
    for c in n["agreement"]["checks"]:
        if c["id"] == "invariant:COURIER_SENT_WITHOUT_DELIVERY":
            assert c["kind"] == "fixture_gap"
    assert {"outcome", "chain_lifecycle", "exit_code_sources", "delivery"} <= ids(n, "agree")
    assert n["derived"] is True and n["custody"] is False


def test_agree_case_with_git_push_delivery_is_clean(tmp_path):
    ref = "refs/heads/night-results/x-night"
    files = go_night(**{"courier.delivery.json": {
        "transport": "git-push", "ref": ref, "commit": "a" * 40, "result_sha256": "b" * 64}})
    n = run(tmp_path, "r1-clean", files)
    assert n["agreement"]["disagreements"] == []


def test_disagree_exit_code_sources(tmp_path):
    files = go_night()
    files["result.json"] = {"verdict": "GO", "chain_exit_code": 0}
    files["chain.exited"] = {"exit_code": 7}
    n = run(tmp_path, "b5-codes", files)
    assert "exit_code_sources" in ids(n)


def test_disagree_exit_without_start(tmp_path):
    files = go_night()
    del files["chain.started"]
    n = run(tmp_path, "b5-nostart", files)
    assert "chain_lifecycle" in ids(n)


def test_disagree_verdict_vs_exit_class(tmp_path):
    files = go_night(exit_code=11)
    files["result.json"]["verdict"] = "REFUSED"
    n = run(tmp_path, "b5-vc", files)
    assert "verdict_vs_exit_class" in ids(n)


def test_gap_nonzero_exit_without_fault_is_writer_candidate(tmp_path):
    n = run(tmp_path, "r1-nofault", go_night(exit_code=3))
    inv = [c for c in n["agreement"]["checks"] if c["id"] == "invariant:NONZERO_EXIT_WITHOUT_FAULT"]
    assert inv and inv[0]["kind"] == "writer_candidate"
    assert n["exit_class"]["tool"] == "r1_runtime" and n["exit_class"]["class"] == "failed"
    assert n["shadow"]["outcome"] == "CHAIN_FAILED"


def test_nonzero_exit_with_fault_reasons_is_module_defect(tmp_path):
    files = go_night(exit_code=11)
    files["hazard_result.json"]["faults"] = {"reasons": ["a", "b"]}
    n = run(tmp_path, "b5-faulted", files)
    inv = [c for c in n["agreement"]["checks"] if c["id"] == "invariant:NONZERO_EXIT_WITHOUT_FAULT"]
    assert inv and inv[0]["kind"] == "module_defect"


def test_disagree_courier_sent_but_no_result_leaves_unknown_outcome(tmp_path):
    n = run(tmp_path, "b5-nores", {"courier.json": GOOD_COURIER, "courier.sent": ""})
    assert "invariant:COURIER_SENT_WITHOUT_RESULT" in ids(n)


def test_missing_files_case(tmp_path):
    n = run(tmp_path, "b5-empty", {})
    assert n["shadow"]["state"] == "UNKNOWN"
    assert "MISSING_RESULT" in n["shadow"]["outcome_reasons"]
    assert ids(n, "agree") >= {"outcome"}
    assert ids(n) == set()


def test_missing_night_dir_listed(tmp_path):
    n = replay.replay_night("gone", None, NOW)
    assert n["missing"] and n["agreement"]["disagreements"][0]["id"] == "night_dir"


def test_refusal_without_chain(tmp_path):
    files = {"result.json": {"verdict": "REFUSED", "chain_exit_code": None}, "refusal.json": {"verdict": "REFUSED"},
             "courier.json": GOOD_COURIER, "courier.sent": ""}
    n = run(tmp_path, "b5-refused", files)
    assert n["shadow"]["outcome"] == "REFUSED_PRE_CHAIN"
    assert "outcome" in ids(n, "agree") and "chain_lifecycle" in ids(n, "agree")
    assert n["recorded"]["chain_started"] is False


def test_refusal_record_with_go_verdict_disagrees(tmp_path):
    files = go_night()
    files["refusal.json"] = {"verdict": "REFUSED"}
    assert "chain_lifecycle" in ids(run(tmp_path, "b5-badref", files))


def test_chain_open_without_result(tmp_path):
    n = run(tmp_path, "b5-open", {"chain.started": {"pid": 1}})
    assert n["shadow"]["state"] == "ChainOpen"
    assert ids(n) == set()


def test_output_is_structure_only_and_restore_note(tmp_path):
    files = go_night(**{"network_time_off.action.json": {"returncode": 0, "stdout": "SECRET-MARKER"}})
    files["result.json"]["energy_j"] = 123456.789
    n = run(tmp_path, "b5-notes", files)
    text = json.dumps(n)
    assert "SECRET-MARKER" not in text and "123456" not in text
    assert "restore_records" in ids(n, "note")
    assert all(e["status"] in {"clear", "unknown", "owed", "explained"} for e in n["owed_effects"])


def test_only_allowlisted_files_are_read(tmp_path):
    d = write(tmp_path, "b5-extra", {**go_night(), "meter_supervision.jsonl": "x", "censuses.jsonl": "x"})
    _, files = replay.load_tree_night(d)
    assert "meter_supervision.jsonl" not in files


def test_cli_writes_json_and_summary(tmp_path):
    write(tmp_path / "tree", "b5-ok", go_night())
    write(tmp_path / "tree", "b5-empty", {})
    out = tmp_path / "out.json"
    assert replay.main(["--tree", str(tmp_path / "tree"), "--out", str(out), "--now", str(NOW)]) == 0
    doc = json.loads(out.read_text())
    assert doc["summary"]["nights"] == 2 and doc["structure_only"] is True


class ShadowReplayTests(unittest.TestCase):
    """Runs each module-level test with a fresh temporary directory (works with unittest or pytest)."""


def _bind(fn):
    def method(self):
        with tempfile.TemporaryDirectory() as tmp:
            fn(Path(tmp))
    method.__name__ = fn.__name__
    return method


for _name, _fn in list(globals().items()):
    if _name.startswith("test_") and callable(_fn):
        setattr(ShadowReplayTests, _name, _bind(_fn))
        del globals()[_name]


if __name__ == "__main__":
    unittest.main()
