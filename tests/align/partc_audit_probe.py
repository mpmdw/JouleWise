"""Audit reproductions for the Part C evaluator, driven through the synthetic launcher.

The reproductions are audit 2's `semantic_probe.py`, rewritten as a regression runner. It loads the frozen
differential suite by path, uses the suite's own clean control, and changes one input before a member's
producer closes. Each damaged attempt must end `other_failure` with its expected reason. Where the frozen
workload disagrees with the damage, the probe first confirms that disagreement itself, so each case is a
contradiction of the frozen code and not only of the evaluator's own rules.

Two cases are positives and must pass: the clean control, and RL-193 section 1's supplement, a predecessor
trace that is the six-column D-018 interval header with zero rows.

    python3.13 -IB tests/align/partc_audit_probe.py [case ...]      (JW_PARTC_REPO selects the tree under test)

It prints one `RESULT <case> <verdict> <reasons>` line per case and exits 1 on any disagreement. The pinned
commits must be in the local object database (see the suite's docstring).
"""
import hashlib
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

SUITE = Path(__file__).resolve().parent / "test_partc_frozen_differential.py"
EXPECTED = {
    "control": None,
    "interval-header-zero-rows": None,
    "raw-runner-fault": "workload_replay",
    "raw-turn-budget-flag": "workload_replay",
    "last-turn-unclosed": "workload_replay",
    "other-run-id": "execution_config",
    "duplicate-predecessor": "sequence",
    "predecessor-timeout": "gate_cardinality",
    "extra-stop-flag": "flag_source",
    "gate-before-entry": "gate_journal_disagreement",
    "finalized-after-close": "member_order",
}


def load_suite():
    spec = importlib.util.spec_from_file_location("partc_suite", SUITE)
    suite = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = suite
    spec.loader.exec_module(suite)
    return suite


def run(argv):
    s = load_suite()
    wanted = argv or list(EXPECTED)
    changed_member = {"raw-runner-fault": s.D, "raw-turn-budget-flag": s.D, "last-turn-unclosed": s.D,
                      "other-run-id": s.X, "duplicate-predecessor": s.S, "predecessor-timeout": s.P,
                      "extra-stop-flag": s.P, "gate-before-entry": s.D, "finalized-after-close": s.D,
                      "interval-header-zero-rows": s.P, "control": None}

    def frozen_refuses(segment, kind):
        try:
            s.check_workload(segment, kind)
        except (s.Disagreement, s.wl.AdapterFailure):
            return True
        return False

    def mutate(case, kind, segment, receipt):
        bundle = segment / receipt["bundle"]
        episode_path = bundle / "outputs/align_episode.json"
        turns_path = bundle / "outputs/align_turns.jsonl"
        episode = s.read(episode_path)
        if case == "interval-header-zero-rows":
            from joulewise.bundle_read import POWER_TRACE_HEADER, POWER_TRACE_INTERVAL_HEADER, _check_power_trace

            trace = bundle / "power_trace.csv"
            assert trace.read_bytes().splitlines()[0].decode() == POWER_TRACE_HEADER
            trace.write_bytes((POWER_TRACE_INTERVAL_HEADER + "\n").encode("ascii"))
            assert _check_power_trace(bundle, s.read(bundle / "summary_metrics.json"),
                                      s.read(bundle / "metadata.json")) == [], "the pinned check refused it"
        elif case in ("last-turn-unclosed", "raw-turn-budget-flag", "raw-runner-fault"):
            turns = s.rows(turns_path)
            assert not episode["turns"][-1]["tool_calls"]
            flag = {"last-turn-unclosed": "unclosed_reasoning_span", "raw-turn-budget-flag": "turn_budget_reached",
                    "raw-runner-fault": "runner.error.synthetic"}[case]
            assert flag not in turns[-1]["flags"]
            turns[-1]["flags"].append(flag)
            s.write_rows(turns_path, turns)
            assert frozen_refuses(segment, kind), "the frozen workload agreed with the damage"
        elif case == "finalized-after-close":
            events_path = bundle / "events.jsonl"
            events = s.rows(events_path)
            close_epoch = s.EPOCH[kind] + 1800
            assert events[-1]["event_type"] == "run_finalized" and events[-1]["timestamp_s"] <= close_epoch
            events[-1]["timestamp_s"] = close_epoch + 1
            s.write_rows(events_path, events)
        elif case == "duplicate-predecessor":
            previous = segment.parent / s.pc.KINDS[s.P]
            extra = previous.with_name(s.r1._fresh_name(segment.parent, previous.name + ".rejected", 1))
            shutil.copytree(previous, extra)
            assert (extra / s.RECEIPT).is_file()
        elif case == "predecessor-timeout":
            assert "thermal" not in episode["hardware"]
            episode["hardware"]["thermal"] = {"intervals": [{"kind": "G0", "turn": 0, "outcome": "timeout"}],
                                              "flags": ["thermal.start_gate_timeout"]}
            s.write(episode_path, episode)
        elif case == "other-run-id":
            assert kind == s.X and bundle.name == "align-v4-r1-x-g"
            other = "align-v4-r1-d-bank-benign-s1"
            config = bundle / "config.json"
            original_digest = hashlib.sha256(config.read_bytes()).hexdigest()
            old, new = bundle.name.encode(), other.encode()
            for rel in ("config.json", "metadata.json", "outputs/align_episode.json", "outputs/align_turns.jsonl",
                        "events.jsonl", "outputs/align_thermal.jsonl"):
                path = bundle / rel
                raw = path.read_bytes()
                if old in raw:
                    path.write_bytes(raw.replace(old, new))
            meta = bundle / "metadata.json"
            meta.write_bytes(meta.read_bytes().replace(
                original_digest.encode(), hashlib.sha256(config.read_bytes()).hexdigest().encode()))
            bundle.rename(bundle.with_name(other))
            receipt["bundle"] = "runs/" + other
            assert s.planned_run_ids()[kind] != other
        elif case == "gate-before-entry":
            path = bundle / "outputs/align_thermal.jsonl"
            rows = s.rows(path)
            for position, row in enumerate(rows):
                if row["kind"] != "align_thermal_gate" or row["values"]["state"] != "begin":
                    continue
                bound = row["values"]["entry_stamp"]["monotonic_before_ns"]
                shift = row["started"]["monotonic_ns"] - (bound - 1_000_000)
                if shift <= 0 or any(row["started"][k] - shift < rows[position - 1]["finished"][k]
                                     for k in row["started"]):
                    continue
                for key in ("started", "finished"):
                    for clock in row[key]:
                        row[key][clock] -= shift
                s.write_rows(path, rows)
                return
            raise AssertionError("no usable synthetic gate bracket")
        elif case == "extra-stop-flag":
            assert not receipt.get("episode_flags")
            receipt["episode_flags"] = ["episode.deadman:0"]
        else:
            raise AssertionError(case)

    failures = []
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        finder = s.import_world(work / "src")
        s.MODEL_DIR = work / "synthetic-model"
        s.MODEL_DIR.mkdir()
        s.write(s.MODEL_DIR / "config.json", {"max_position_embeddings": 40960})
        s.issue_model_source()
        s.endpoint_code()
        with s.kit_source(finder), s.compact_control(), patch.object(
                s.rt, "registered_s6", return_value={"slots": {"S6": 1.}, "s6_tuning": {}}):
            for name in wanted:
                changed = changed_member[name]
                terminal, published = s.fixture.write_terminal, s.published
                edits, verdicts = [], []

                def close(segment, kind, receipt, sha):
                    if kind == changed:
                        mutate(name, kind, segment, receipt)
                        edits.append(kind)
                    return terminal(segment, kind, receipt, sha)

                def observe(case, rc):
                    verdict = published(case, rc)
                    record = s.read(case.attempt.output / "smoke.json")["evaluation"]
                    verdicts.append((verdict, record["pass"], rc, sorted(record["evidence_failures"])))
                    return verdict

                with patch.object(s.fixture, "write_terminal", close), patch.object(s, "published", observe):
                    try:
                        s.control(work / name)
                    except s.Disagreement as error:
                        if not str(error).startswith("clean control: "):
                            raise
                assert edits == ([changed] if changed else []) and len(verdicts) == 1, (name, edits, verdicts)
                verdict, passed, code, reasons = verdicts[0]
                expected = EXPECTED[name]
                ok = (verdict, passed, code) == ("pass", True, 0) if expected is None else (
                    (verdict, passed, code) == ("other_failure", False, 2) and expected in reasons)
                print("RESULT", name, verdict, ",".join(reasons) or "-", flush=True)
                if not ok:
                    failures.append(name)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
