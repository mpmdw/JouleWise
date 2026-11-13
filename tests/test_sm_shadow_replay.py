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

import atexit
import shutil

_TMP = Path(tempfile.mkdtemp(prefix="sm-shadow-test-"))
atexit.register(shutil.rmtree, _TMP, True)
replay.TMP_ROOT = _TMP  # tests never touch the SSD scratch root

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
            assert c["kind"] == "input_gap"
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
    assert n["exit_class"]["tool"] == "b5_chain"  # explicit non-ALIGN family keeps b5_chain
    assert n["shadow"]["outcome"] == "CHAIN_FAILED"


def test_align_r1_chain_is_read_under_r1_driver_exit_3_is_refused(tmp_path):
    n = run(tmp_path, "align-r1-20261111T0208Z", go_night(exit_code=3))
    assert n["exit_class"]["tool"] == "r1_driver" and n["exit_class"]["class"] == "refused"
    assert replay.chain_contract_for("r1-alpha") == "b5_chain"
    assert replay.chain_contract_for("align-pilot-1") == "unknown"


def test_non_align_ref_is_skipped_by_default_and_named_family_is_explicit(tmp_path):
    write(tmp_path / "tree", "b5-ok", go_night())
    write(tmp_path / "tree", "r1-alpha", go_night())
    write(tmp_path / "tree", "align-r1-x", go_night())
    write(tmp_path / "tree", "align-pilot-y", go_night())
    out = tmp_path / "out.json"
    assert replay.main(["--tree", str(tmp_path / "tree"), "--out", str(out), "--now", str(NOW)]) == 0
    doc = json.loads(out.read_text())
    assert [r["night"] for r in doc["summary"]["rows"]] == ["align-pilot-y", "align-r1-x"]
    assert doc["skipped_by_family_gate"] == 2
    assert replay.main(["--tree", str(tmp_path / "tree"), "--family", "b5-", "--out", str(out), "--now", str(NOW)]) == 0
    assert [r["night"] for r in json.loads(out.read_text())["summary"]["rows"]] == ["b5-ok"]


def test_go_verdict_masking_chain_failure_is_listed(tmp_path):
    n = run(tmp_path, "r1-mask", go_night(exit_code=3))
    mask = [c for c in n["agreement"]["checks"] if c["id"] == "verdict_masks_outcome"]
    assert mask and mask[0]["status"] == "disagree" and mask[0]["kind"] == "writer_candidate"
    assert "verdict_masks_outcome" not in ids(run(tmp_path, "r1-nomask", go_night()))


def test_w1_style_record_does_not_trigger_verdict_mask(tmp_path):
    files = go_night(exit_code=5)
    for k in ("result.json", "hazard_result.json"):
        files[k].update({"chain_outcome": "CHAIN_FAILED", "fault": True, "fault_reasons": ["chain_exit_nonzero:5"]})
    n = run(tmp_path, "align-r1-w1", files)
    assert "verdict_masks_outcome" not in ids(n)
    assert "recorded_chain_outcome" in ids(n, "agree")
    assert "invariant:NONZERO_EXIT_WITHOUT_FAULT" not in ids(n)


def test_w1_style_record_with_wrong_chain_outcome_disagrees(tmp_path):
    files = go_night(exit_code=5)
    files["result.json"]["chain_outcome"] = "COMPLETE"
    assert "recorded_chain_outcome" in ids(run(tmp_path, "align-r1-w1b", files))


def test_legacy_record_without_chain_outcome_still_masks(tmp_path):
    assert "verdict_masks_outcome" in ids(run(tmp_path, "align-r1-old", go_night(exit_code=3)))


def test_reasons_without_boolean_is_legacy_schema_gap(tmp_path):
    files = go_night(exit_code=11)
    files["hazard_result.json"]["faults"] = {"reasons": ["a", "b"]}
    n = run(tmp_path, "b5-faulted", files)
    inv = [c for c in n["agreement"]["checks"] if c["id"] == "invariant:NONZERO_EXIT_WITHOUT_FAULT"]
    assert inv and inv[0]["kind"] == "legacy_schema_gap"


def test_boolean_false_with_nonzero_exit_stays_a_violation(tmp_path):
    files = go_night(exit_code=11)
    files["result.json"]["fault"] = False
    files["hazard_result.json"].update({"fault": False, "faults": {"reasons": ["a"]}})
    n = run(tmp_path, "b5-boolfalse", files)
    inv = [c for c in n["agreement"]["checks"] if c["id"] == "invariant:NONZERO_EXIT_WITHOUT_FAULT"]
    assert inv and inv[0]["kind"] == "writer_candidate"
    n2 = run(tmp_path, "b5-boolfalse2", {**go_night(exit_code=11), "result.json": {"verdict": "GO", "chain_exit_code": 11, "fault": False}})
    assert "invariant:NONZERO_EXIT_WITHOUT_FAULT" in ids(n2)


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


def test_no_non_allowlisted_key_or_content_reaches_temp_dir_or_output(tmp_path):
    files = go_night(**{"network_time_off.action.json": {"returncode": 0, "stdout": "SECRET-STDOUT"},
                        "courier.json": {"sent": True, "message_id": "MSGID-SECRET"},
                        "chain.exit-census.json": {"survivors": [{"cmd": "SECRET-CMD"}]},
                        "censuses.jsonl": "SECRET-CENSUS", "go-census.json": "SECRET-GO"})
    files["result.json"].update({"energy_j": 123456.789, "note": "SECRET-NOTE", "fault_reasons": ["SECRET-REASON"]})
    files["hazard_result.json"].update({"meter": {"watts": 987654.321}, "monitor": "SECRET-MON",
                                        "faults": {"reasons": ["SECRET-R2"], "detail": "SECRET-D"}})
    d = write(tmp_path, "align-r1-secret", files)
    _, loaded = replay.load_tree_night(d)
    blob = b"".join(loaded.values()).decode()
    assert not any(x in blob for x in ("SECRET", "123456", "987654"))
    assert loaded["censuses.jsonl"] == b"" and loaded["go-census.json"] == b""
    seen = []
    orig = replay.window_state.observe_night_dir

    def spy(root, *a, **k):
        for p in Path(root).rglob("*"):
            if p.is_file():
                seen.append(p.read_text())
        return orig(root, *a, **k)
    replay.window_state.observe_night_dir = spy
    try:
        n = replay.replay_night("align-r1-secret", loaded, NOW)
    finally:
        replay.window_state.observe_night_dir = orig
    assert seen and not any(x in "".join(seen) for x in ("SECRET", "123456", "987654", "energy_j", "meter"))
    assert not any(x in json.dumps(n) for x in ("SECRET", "123456", "987654"))


def test_existence_files_are_never_fetched_from_git(tmp_path):
    calls = []
    orig = replay._git

    class R:
        def __init__(self, out, rc=0):
            self.stdout, self.returncode = out, rc

    def fake(args, cwd):
        calls.append(args)
        if args[0] == "ls-tree":
            return R(b"censuses.jsonl\nresult.json\nrestore.json\n")
        return R(b'{"verdict": "GO", "x": "SECRET"}')
    replay._git = fake
    try:
        _, files = replay.load_git_night("origin/night-results/align-r1-q", tmp_path)
    finally:
        replay._git = orig
    shown = [c[1] for c in calls if c[0] == "show"]
    assert shown and all(s.endswith("/result.json") for s in shown)
    assert files["censuses.jsonl"] == b"" and "SECRET" not in files["result.json"].decode()
    assert "restore.json" in files.all_names


def test_restore_check_sees_names_in_full_listing(tmp_path):
    d = write(tmp_path, "align-r1-a", go_night(**{"network_time_off.json": {"x": 1}}))
    _, loaded = replay.load_tree_night(d)
    rec = replay.recorded_facts(loaded)
    assert rec["network_time_off_action_record"] and not rec["restore_record_in_delivered_tree"]
    d2 = write(tmp_path, "align-r1-b", go_night(**{"network_time_off.json": {}, "ntp_restore.json": {}}))
    _, loaded2 = replay.load_tree_night(d2)
    assert replay.recorded_facts(loaded2)["restore_record_in_delivered_tree"]


def test_cli_writes_json_and_summary(tmp_path):
    write(tmp_path / "tree", "b5-ok", go_night())
    write(tmp_path / "tree", "b5-empty", {})
    out = tmp_path / "out.json"
    assert replay.main(["--tree", str(tmp_path / "tree"), "--family", "b5-", "--out", str(out), "--now", str(NOW)]) == 0
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
