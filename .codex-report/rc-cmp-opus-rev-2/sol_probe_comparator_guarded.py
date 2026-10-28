"""Synthetic-only adversarial probes for RC-CMP-SOL-REV."""
import contextlib
import io
import json

from independent_recompute import test_comparator as tc
from independent_recompute import test_comparator_meter as tm


def failures(result):
    return {k: v["fail"] for k, v in result["counts"].items() if v["fail"]}


case = tc.ComparatorTests("test_baseline_agrees_under_both_bar_sets")
case.setUp()
try:
    baseline = case.run_compare(rules=tc.RULES)
    print("baseline", failures(baseline), baseline["coverage"]["unmapped"])
    finite_rows = []
    for value in (None, float("nan"), float("inf"), -float("inf")):
        c = tc.cmp.Comparison(tc.cmp.load_bars(tc.cmp.DEFAULT_BARS))
        finite_rows.append((str(value), c.numeric("contrast_j", "probe", 1.0, value)["verdict"]))
    print("nonfinite_or_null", finite_rows)

    run_name = "rereduced/alpha/run-a.rereduced.json"
    removed = case.files.pop(run_name)
    result = case.run_compare(rules=tc.RULES)
    print("missing_l9_run_output", failures(result), result["counts"]["run_phase_energy_j"],
          "recompute_request=", case.ours["members"]["ALPHA"]["run-a"]["E_j"]["request"])
    tc.cmp.COVERAGE = tc.RULES
    one_side_input = case.root / "one-side-ours.json"
    one_side_input.write_text(json.dumps(case.ours))
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        rc = tc.cmp.main(["--l9-custody", str(case.custody()), "--recompute", str(one_side_input),
                          "--restricted-out", str(case.root / "one-side-result.json")])
    print("missing_l9_run_cli", rc)
    case.files[run_name] = removed

    case.ours["members"]["ALPHA"]["extra-run"] = {"E_j": {"prefill": 900., "decode": 900., "request": 900.}}
    result = case.run_compare(rules=tc.RULES)
    print("extra_recompute_run", failures(result), result["counts"]["run_phase_energy_j"])
    del case.ours["members"]["ALPHA"]["extra-run"]

    # The value belongs to the contrast_j family, but to the CI lower leaf,
    # not to this contrast's estimate. Both L9's verdict and ours say -1.25.
    fill = case.files[f"outputs/{tc.SHA}-results-fill-input.json"]
    fill["gamma"]["contrasts"][0]["estimate"] = -13.5
    result = case.run_compare(rules=tc.RULES)
    path = "fill:gamma/contrasts/*/estimate"
    print("wrong_fill_estimate", failures(result), result["coverage"]["unmapped"], result["coverage"]["leaves"].get(path),
          "fill=", fill["gamma"]["contrasts"][0]["estimate"], "recompute=", case.ours["contrasts"][tc.DECODE]["dbar_j"])
    tc.cmp.COVERAGE = tc.RULES
    public, error = io.StringIO(), io.StringIO()
    comparison_input = case.root / "wrong-fill-ours.json"
    comparison_input.write_text(json.dumps(case.ours))
    with contextlib.redirect_stdout(public), contextlib.redirect_stderr(error):
        rc = tc.cmp.main(["--l9-custody", str(case.custody()), "--recompute", str(comparison_input),
                          "--restricted-out", str(case.root / "wrong-fill-result.json")])
    print("wrong_fill_cli", rc, "stderr=", error.getvalue().strip())
    fill["gamma"]["contrasts"][0]["estimate"] = -1.25

    # Per-key override parser validates only `match`, not the override bar.
    bars = json.loads(tc.BARS["recompute_coded_7e322b76"].read_text())
    bars["families"]["contrast_j"]["keys"] = [{"match": ".*", "absolute": float("inf")}]
    path = case.root / "bad-bars.json"
    path.write_text(json.dumps(bars))
    case.ours["contrasts"][tc.DECODE]["dbar_j"] = 1000.0
    ours = case.root / "ours.json"
    ours.write_text(json.dumps(case.ours))
    try:
        result = tc.cmp.run(case.custody(), ours, path, tc.RULES)
        row = next(r for r in result["comparisons"] if r["key"] == tc.DECODE + "/dbar_j")
        print("infinite_override", failures(result), row["verdict"], row["bar"])
    except tc.cmp.Refusal as exc:
        print("infinite_override REFUSED", exc)
    missing = json.loads(tc.cmp.DEFAULT_BARS.read_text())
    del missing["families"]["contrast_j"]
    missing_path = case.root / "missing-bars.json"
    missing_path.write_text(json.dumps(missing))
    try:
        tc.cmp.load_bars(missing_path)
    except tc.cmp.Refusal as exc:
        print("family_absent", str(exc))
    case.ours["contrasts"][tc.DECODE]["dbar_j"] = -1.25

    # Public CLI counts flip with a planted energy value.
    tc.cmp.COVERAGE = tc.RULES
    def cli():
        out, err = io.StringIO(), io.StringIO()
        restricted = case.root / "comparison.json"
        restricted.unlink(missing_ok=True)
        ours.write_text(json.dumps(case.ours))
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = tc.cmp.main(["--l9-custody", str(case.custody()), "--recompute", str(ours),
                              "--restricted-out", str(restricted)])
        line = out.getvalue().splitlines()[0]
        counts = json.loads(line.split(" families=", 1)[1].split(" step11_", 1)[0])
        return rc, counts["run_phase_energy_j"], err.getvalue().strip()
    print("public_counts_before", cli())
    case.ours["members"]["ALPHA"]["run-a"]["E_j"]["decode"] += 0.01
    print("public_counts_after", cli())
finally:
    case.tmp.cleanup()

tm.MeterLineTests.setUpClass()
meter = tm.MeterLineTests("test_meter_line_agrees_and_is_covered")
meter.setUp()
try:
    result = meter.compare()
    print("meter_baseline", failures(result), result["coverage"]["unmapped"])
    line = meter.case.files[f"disclosures/{tc.SHA}.json"]["window_lines"]["alpha"][1]
    line["median"] += 1.0
    result = meter.compare()
    print("wrong_machine_median", failures(result), result["coverage"]["unmapped"],
          result["coverage"]["leaves"].get("disclosure:window_lines/alpha/*/median"),
          "median=", line["median"], "member_rho=", meter.record["members"][meter.rid]["rho"])
    tm.cmp.COVERAGE = tm.RULES + tm.MACHINE_RULES
    public, error = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(public), contextlib.redirect_stderr(error):
        rc = tm.cmp.main(["--l9-custody", str(meter.case.custody()),
                          "--recompute", str(meter.case.root / "ours.json"),
                          "--harvest-meter", "alpha=" + str(meter.case.root / "harvest-meter.json"),
                          "--restricted-out", str(meter.case.root / "wrong-median-result.json")])
    print("wrong_machine_median_cli", rc, "stderr=", error.getvalue().strip())
    saved = meter.record["members"].pop(meter.rid)
    result = meter.compare()
    print("missing_harvest_member", failures(result), result["counts"]["meter_j"],
          "disclosed_members=", len(meter.case.files[f"disclosures/{tc.SHA}.json"]["window_lines"]["alpha"]))
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        rc = tm.cmp.main(["--l9-custody", str(meter.case.custody()),
                          "--recompute", str(meter.case.root / "ours.json"),
                          "--harvest-meter", "alpha=" + str(meter.case.root / "harvest-meter.json"),
                          "--restricted-out", str(meter.case.root / "missing-harvest-result.json")])
    print("missing_harvest_member_cli", rc)
    meter.record["members"][meter.rid] = saved
    saved_machine = meter.record["members"][meter.rid].pop("machine")
    result = meter.compare()
    print("missing_harvest_machine", failures(result), result["counts"]["meter_j"])
    meter.record["members"][meter.rid]["machine"] = saved_machine
    no_meter = meter.compare(meter=False)
    print("no_harvest_meter", failures(no_meter))
finally:
    meter.case.tmp.cleanup()
    tm.MeterLineTests.tearDownClass()
