"""RL-215's named Part C checks on the frozen v4 control: the outer soak row absent, and the marker test.

Q2, outer row absent. An archive with no soak ledger binds the soak to archived custody (RLD:20789, 20613): no row
is invented and the three outer comparisons (EVIDENCE-INVARIANTS ``outer-open``, ``outer-close``, ``outer-next``)
are not made, while the members' own terminal-order checks still apply. An archive that holds the row is compared
as native. A native run without the row is ``evidence_unverifiable`` (RLD:20771).

Builder item 8, RL-183c test 3 (RLD:20654) extended to the new class rules: a marker planted in the values the
battery count and callback order, the excluded PID in both census snapshots, the gated status wire, its clocks and
PM cache, the SMC raw reading and the inventory sweep read appears in no finding and in no emitted line.

The frozen v4 suite builds its writer-produced control and imports the pinned R1 sources; each case then changes
only what it names. Every byte is synthetic.

    python3.13 -IB tests/align/partc_rl215_checks.py [case ...]   (JW_PARTC_REPO selects the tree under test)

It prints one ``RESULT <case> <verdict> <reasons>`` line per case and exits 1 on any disagreement. The pinned
commits must be in the local object database (see the suite's docstring).
"""
import importlib.util
import json
import shutil
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

SUITE = Path(__file__).resolve().parents[2] / "tests/frozen/partc-v4/suite-v4/tests/align/test_partc_writer_v4.py"
MARKER = 918273645672
EXPECTED = {
    "archive-with-row": "pass -",
    "archive-without-row": "pass -",
    "archive-without-row-overlapping-member": "other_failure member_order",
    "archive-row-without-reference": "other_failure evidence_unverifiable",
    "native-without-row": "other_failure evidence_unverifiable",
    "marker-class-rules": "no-value battery_evidence,load_evidence,reading_record,step_thermometry",
}


def load_suite():
    spec = importlib.util.spec_from_file_location("partc_v4_rl215", SUITE)
    suite = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = suite
    spec.loader.exec_module(suite)
    return suite


def marker_case(s, work):
    """Refuse each new class rule on planted values, publish the findings, and search everything released."""
    pc, failure_type = s.pc, s.evidence.EvidenceFailure
    failures = []

    def collect(call):
        try:
            call()
        except failure_type as error:
            failures.append(error)
        else:
            raise AssertionError("a planted check passed")

    def raw(value):
        return json.dumps(value).encode()

    marked = float(MARKER)
    census = [{"label": "start", "t_s": marked, "processes": []},
              {"label": "end", "t_s": marked + 90, "processes": []}]
    load = {"cpu_busy_t_s": [1.0, 2.0], "cpu_busy_cores": [0.0, 0.0], "errors": [], "census": census}
    # Battery cardinality: three rows for two ticks at period 30.
    collect(lambda: pc._check_callbacks([{"epoch_s": marked}] * 3, load, "x-g", {}, 30, None))
    # The opening sample after the bound work began.
    collect(lambda: pc._check_callbacks([{"epoch_s": marked + 5}, {"epoch_s": marked + 6}], load, "x-g",
                                        {"events.jsonl": raw({"timestamp_s": marked + 1})}, 30, None))
    # The opening sample before its census, through a planted zero-width paired stamp.
    episode = raw({"hardware": {"paired_clock_stamps_ns": [
        {"epoch_ns": MARKER, "monotonic_before_ns": MARKER, "monotonic_after_ns": MARKER}]}})
    collect(lambda: pc._check_callbacks(
        [{"epoch_s": (MARKER - 1) / 1e9}, {"epoch_s": marked + 99}],
        {**load, "census": [dict(census[0], t_s=MARKER / 1e9), dict(census[1], t_s=MARKER / 1e9 + 90)]},
        "x-g", {"outputs/align_episode.json": episode}, 30, None))
    # The live runtime PID absent from the closing census snapshot.
    journal = {"exclude_roots": [MARKER], "errors": [], "cpu_busy_cores": [0.0], "cpu_busy_t_s": [1.0],
               "census": [{"label": "start", "t_s": 10.0, "processes": [
                              {"pid": MARKER, "ppid": 1, "pcpu": marked, "comm": str(MARKER)}]},
                          {"label": "end", "t_s": 20.0, "processes": [
                              {"pid": MARKER + 1, "ppid": 1, "pcpu": marked, "comm": str(MARKER)}]}]}
    receipt = {"load_journal_errors": [], **{key: journal[key] for key in ("cpu_busy_cores", "cpu_busy_t_s",
                                                                            "census")}}
    collect(lambda: pc._check_load(raw(journal), receipt, "x-g"))
    # The gated status: an error with siblings, a PM stamp after its status stamp, a status stamp before the read
    # finished, and a cached stamp whose state changed.
    source = pc.THERMAL_SOURCE
    collect(lambda: pc._check_gated_status({"error": str(MARKER), "os_level": MARKER}, 0, None, "x-g", source, 1))
    collect(lambda: pc._check_gated_status({"os_level": MARKER, "pm_state": str(MARKER),
                                            "pm_observed_ns": MARKER + 1, "monotonic_ns": MARKER}, 0, None,
                                           "x-g", source, 1))
    collect(lambda: pc._check_gated_status({"os_level": 0, "pm_state": None, "pm_observed_ns": None,
                                            "monotonic_ns": MARKER}, MARKER + 1, None, "x-g", source, 1))
    collect(lambda: pc._check_gated_status({"os_level": 0, "pm_state": str(MARKER + 1),
                                            "pm_observed_ns": MARKER - 9, "monotonic_ns": MARKER}, MARKER - 1,
                                           (MARKER - 9, str(MARKER)), "x-g", source, 1))
    # An SMC success whose bytes decode to another value, inside an inventory sweep.
    entry = {"data_type": "sp78", "data_size": 2, "raw_hex": "2300", "value": marked, "error": None}
    assert not pc._smc_entry_ok("TV0h", entry)
    sweep = {"started": {"monotonic_ns": MARKER}, "finished": {"monotonic_ns": MARKER}, "phase": None, "seq": 1,
             "values": {"source": "smc", "sensors": {"TV0h": marked}, "units": {"TV0h": "degC"}, "errors": {},
                        "readings": {"TV0h": entry}}}
    collect(lambda: pc._check_inventory_sweep(sweep, ["TV0h"], 0))

    output = work / "marker-part-c"
    output.mkdir()
    stdout, stderr = StringIO(), StringIO()
    released = []
    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            pc._emit_part_c(output, 0, None, failures=tuple(failures))
        except ValueError as error:
            released.append(str(error))
        else:
            raise AssertionError("a refused publication passed")
    released += [stdout.getvalue(), stderr.getvalue(), *[(output / name).read_text() for name in pc.RELEASE_COPIES],
                 *[json.dumps(failure.finding()) for failure in failures]]
    findings = [line for line in stdout.getvalue().splitlines() if line.startswith("{")]
    leaked = any(str(MARKER)[:9] in text for text in released) or len(findings) != len(failures)
    return f"{'leaked' if leaked else 'no-value'} {','.join(sorted({failure.reason for failure in failures}))}"


def run(argv):
    wanted = argv or list(EXPECTED)
    assert all(name in EXPECTED for name in wanted), "unknown case"
    s = load_suite()
    seen = {}
    with tempfile.TemporaryDirectory(prefix="jw-v4-rl215-") as tmp:
        root = Path(tmp)
        with s.v4_context(root):
            if "marker-class-rules" in wanted:
                seen["marker-class-rules"] = marker_case(s, root)
            if set(wanted) - {"marker-class-rules"}:
                base = root / "base"
                assert s.control(base) == [], "four descriptor bindings required"
                probe = s.Probe(base)
                assert probe.candidate(None), "the clean native control must pass"
                native = probe.tree / "native" / "synthetic-run"
                config = s.rt.ROOT / s.r1.DEFAULT_RUNTIME_CONFIG

                def archive(name, edit):
                    copy = root / name / "synthetic-run"
                    shutil.copytree(native, copy)
                    edit(copy)
                    result = s.pc.replay_archived(copy / "part-c", config)
                    assert result["binding"] == "archived_custody", result
                    seen[name] = f"{result['verdict']} {','.join(result['evidence_failures']) or '-'}"

                def without_row(copy, *, reference=False):
                    (copy / "soak" / "soak_row.json").unlink()
                    if not reference:
                        (copy / "soak" / "soak_reference.json").unlink()

                def overlapping(copy):
                    without_row(copy)
                    idle = s.read(copy / "soak" / "idle_soak" / s.rt.CUSTODY_NAME)
                    member = copy / "part-c" / s.pc.KINDS[s.P]
                    terminal = s.read(member / s.rt.CUSTODY_NAME)
                    terminal["started_epoch_s"] = idle["ended_epoch_s"] - 1
                    s.write(member / s.rt.CUSTODY_NAME, terminal)

                edits = {"archive-with-row": lambda copy: None, "archive-without-row": without_row,
                         "archive-without-row-overlapping-member": overlapping,
                         "archive-row-without-reference": lambda copy: without_row(copy, reference=True)}
                for name, edit in edits.items():
                    if name in wanted:
                        archive(name, edit)
                if "native-without-row" in wanted:
                    # The launcher bound the row by digest in the soak ledger; it is gone at Part C.
                    (native / "soak" / "soak_row.json").unlink()
                    accepted = probe.candidate(None)
                    evaluation = json.loads((native / "part-c" / "smoke.json").read_text())["evaluation"]
                    seen["native-without-row"] = (f"{evaluation['verdict']} "
                                                  f"{','.join(sorted(evaluation['evidence_failures'])) or '-'}")
                    assert not accepted or evaluation["verdict"] == "pass"
    failures = 0
    for name in wanted:
        print("RESULT", name, seen.get(name, "missing"), flush=True)
        failures += seen.get(name) != EXPECTED[name]
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
