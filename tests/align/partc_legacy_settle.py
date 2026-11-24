"""RL-215 Q5: settle each inherited must-refuse operand the legacy run admitted, by the frozen oracle on v4 bytes.

"An admitted `must refuse` ID is settled by the frozen oracle on the v4 bytes, never by the evaluator: a mismatch
is a false pass; none makes it `may pass (control changed)`, listed by ID." The frozen v4 suite's normalized runner
(`legacy/normalized_v32.py`) prints such an ID as FALSE_PASS; this runner applies the suite's own oracle
(`Probe.oracle`, the frozen checks and driver on the mutated v4 bytes) to it, and prints both paths beside it.

    python3.13 -IB tests/align/partc_legacy_settle.py IDS_FILE      (one legacy ID per line)

It prints one ``SETTLE <id> | <expected> | native ... | archive ... | oracle admits|refuses`` line per ID; an
``oracle admits`` ID is `may pass (control changed)`, an ``oracle refuses`` ID stays a false pass. Every byte is
synthetic. The pinned commits must be in the local object database (see the suite's docstring).
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

RUNNER = Path(__file__).resolve().parents[2] / "tests/frozen/partc-v4/suite-v4/legacy/normalized_v32.py"


def main(path):
    names = [line.rstrip("\n") for line in open(path) if line.strip()]
    spec = importlib.util.spec_from_file_location("partc_legacy_settle", RUNNER)
    runner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = runner
    spec.loader.exec_module(runner)
    s = runner.module()
    cases = {case.name: (case, expected) for case, expected in runner.operands(s) if case.name in names}
    assert set(cases) == set(names), "unknown legacy ID"
    if not names:
        return 0
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
                print("SETTLE", name, "|", expected,
                      "| native", native["verdict"], ",".join(sorted(native["evidence_failures"])) or "-",
                      "| archive", archive["verdict"], ",".join(archive["evidence_failures"]) or "-",
                      "| oracle", "admits" if oracle is None else "refuses", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
