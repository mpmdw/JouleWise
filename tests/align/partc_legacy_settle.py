"""RL-215 Q5 as RL-216 R1 amends it: settle each inherited must-refuse operand the legacy run admitted.

RL-215 Q5: "An admitted `must refuse` ID is settled by the frozen oracle on the v4 bytes, never by the evaluator: a
mismatch is a false pass; none makes it `may pass (control changed)`, listed by ID." RL-216 R1 adds a second closed
list, ``archive_unattested``: the four ``max_position_embeddings/shift`` IDs, whose archive pass is RL-189 §1.4's
ruled ``native_limit: unattested`` outcome. Each of the four is settled so only if all three hold:

  1. native: ``other_failure`` with ``admission_recompute`` among its reasons;
  2. archive: ``pass``, no reason, and ``native_limit`` ``unattested`` for all four members;
  3. oracle: refuses, with the label ``native context limits.max_position_embeddings``.

One condition failing on one of the four, or any other admitted ID the oracle refuses, is a false pass. The frozen v4
suite's normalized runner (``legacy/normalized_v32.py``) prints every such ID as FALSE_PASS; this runner applies the
suite's own oracle (``Probe.oracle``, the frozen checks and driver on the mutated v4 bytes) and prints both paths.

    python3.13 -IB tests/align/partc_legacy_settle.py IDS_FILE      (one legacy ID per line)

``JW_PARTC_ARCHIVE_UNATTESTED`` (a JSON list) is the closed list; without it the built-in RL-216 list is used. It
prints one ``SETTLE <category> <id> <json>`` line per ID, the category being ``control_changed``,
``archive_unattested`` or ``false_pass``, and exits 1 if any ID is a false pass. Every byte is synthetic. The pinned
commits must be in the local object database (see the suite's docstring).
"""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

RUNNER = Path(__file__).resolve().parents[2] / "tests/frozen/partc-v4/suite-v4/legacy/normalized_v32.py"
# RL-216 R1: the closed archive_unattested list, by ID.
ARCHIVE_UNATTESTED = tuple(
    f"{member}/runs/{bundle}/outputs/align_episode.json/hardware.context_limits.max_position_embeddings/shift"
    for member, bundle in (("capture-predecessor-30b", "align-pilot-v3-episodes-a-e01"), ("step-d", "align-v4-r1-step-d"),
                           ("d-bank-benign-s1", "align-v4-r1-d-bank-benign-s1"), ("x-g", "align-v4-r1-x-g")))
ORACLE_LABEL = "native context limits.max_position_embeddings"
MEMBERS = ("capture-predecessor-30b", "step-d", "d-bank-benign-s1", "x-g")


def category(name, record, closed):
    """RL-215 Q5 with RL-216 R1: the settlement of one admitted must-refuse ID."""
    if name in closed:
        conditions = (record["native_verdict"] == "other_failure" and "admission_recompute" in record["native_reasons"],
                      record["archive_verdict"] == "pass" and not record["archive_reasons"]
                      and not record["archive_checks"]
                      and record["native_limit"] == dict.fromkeys(MEMBERS, "unattested"),
                      record["oracle"] == "refuses" and record["oracle_label"] == ORACLE_LABEL)
        record["conditions"] = list(conditions)
        return "archive_unattested" if all(conditions) else "false_pass"
    return "control_changed" if record["oracle"] == "admits" else "false_pass"


def main(path):
    names = [line.rstrip("\n") for line in open(path) if line.strip()]
    closed = tuple(json.loads(os.environ["JW_PARTC_ARCHIVE_UNATTESTED"])) if os.environ.get(
        "JW_PARTC_ARCHIVE_UNATTESTED") else ARCHIVE_UNATTESTED
    assert sorted(closed) == sorted(ARCHIVE_UNATTESTED), "the archive_unattested list is closed by RL-216 R1"
    spec = importlib.util.spec_from_file_location("partc_legacy_settle", RUNNER)
    runner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = runner
    spec.loader.exec_module(runner)
    s = runner.module()
    cases = {case.name: (case, expected) for case, expected in runner.operands(s) if case.name in names}
    assert set(cases) == set(names), "unknown legacy ID"
    if not names:
        return 0
    unsettled = 0
    with tempfile.TemporaryDirectory(prefix="jw-v4-settle-") as tmp:
        with s.v4_context(Path(tmp)):
            base = Path(tmp) / "base"
            assert not s.control(base)
            probe = s.Probe(base)
            s.WORKER = s.ORIGINAL = probe
            assert s.issued_verdict(probe)["pass"] and probe.candidate(None)
            for name in names:
                case, expected = cases[name]
                probe.candidate(case)
                output = probe.tree / "native/synthetic-run/part-c"
                for role in (s.P, s.S, s.D, s.X):
                    if not (output / s.pc.KINDS[role]).exists():
                        s.copy_segment(base, role, output / s.pc.KINDS[role])
                native = s.read(output / "smoke.json")["evaluation"]
                archive = s.pc.replay_archived(output, s.rt.ROOT / s.r1.DEFAULT_RUNTIME_CONFIG)
                try:
                    oracle = probe.oracle(case)
                except Exception as error:  # noqa: BLE001 - an oracle that cannot decide does not admit
                    oracle = f"raised {type(error).__name__}"
                record = {"expected": expected, "native_verdict": native["verdict"],
                          "native_reasons": sorted(native["evidence_failures"]), "archive_verdict": archive["verdict"],
                          "archive_reasons": archive["evidence_failures"], "archive_checks": archive["failing_checks"],
                          "native_limit": archive["native_limit"], "oracle": "admits" if oracle is None else "refuses",
                          "oracle_label": oracle}
                settled = category(name, record, closed)
                unsettled += settled == "false_pass"
                print("SETTLE", settled, name, json.dumps(record, sort_keys=True), flush=True)
    return 1 if unsettled else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
