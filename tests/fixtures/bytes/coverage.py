"""Adapted Opus p03: identical member redraw/seeds, HC3 and OLS coverage.

Source: JouleWise-data 6039fff:review/opus/repro/p03_h2_coverage.py.
Used by tests.test_bytes_analysis.Addendum4RegressionTests.test_a4_05_p03_coverage.
Run with python3.13 tests/fixtures/bytes/coverage.py CAMPAIGN 400.
"""
from __future__ import annotations
import json
import math
import random
import statistics
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from joulewise import bytes_analysis as ba
from joulewise.analysis_engine.distributions import student_t_quantile as tq


def run(base, R=400):
    manifest = ba.read_json(Path(base) / "manifest.json")
    records = ba.load_records(Path(base) / "export", manifest, stage="all")
    spec = {m["model"]: m for m in manifest["models"]}
    report = []
    # R3 uses mean E / mean T. Use the fixture's actual two-pass durations
    # (the main campaign doubles pass 2), not the equal-pass pilot duration.
    pass_cells = ba.reduce_models(records, manifest, boundaries=("rails",))
    durations = {p["model"]: p["duration_s"] for p in ba.combine_passes(pass_cells)
                 if p["basis"] == "gross primary"}
    def truth_e(world, m, duration=None):
        b = (m["W_bytes"] + m["KV_bytes"]) / 1e9
        tau = (durations[m["model"]] if duration is None else duration) / 512
        return .01 * b if world == "bytes" else 3 * tau if world == "time" else .01 * m["R_bytes"] / 1e9


    def population_eps(world, factor):
        xs = [(m["W_bytes"] + m["KV_bytes"]) / 1e9 * 512 / durations[m["model"]] for m in manifest["models"]]
        ys = [truth_e(world, m) * 512 / durations[m["model"]] for m in manifest["models"]]
        mx, my = statistics.fmean(xs), statistics.fmean(ys)
        return factor * math.fsum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.fsum((x - mx) ** 2 for x in xs)


    def redraw(world, rng):
        out = []
        for r in records:
            m = spec[r["model"]]
            e = truth_e(world, m, r["duration_s"]) * 512 * (1 + rng.gauss(0, .002))
            idle_rails = r["rails_j"] - r["rails_secondary_j"]
            meter = dict(r["meter"])
            meter["gross_j"] = 2 * e
            meter["secondary_j"] = 2 * e - (r["meter"]["gross_j"] - r["meter"]["secondary_j"])
            # p03 deliberately redraws conditional energies, without native
            # timing flips. Recompute the offset inputs for these new powers;
            # the 60 CLI campaigns separately exercise the physical offset.
            power = 2 * e / r["duration_s"]
            meter["edge_powers_w"] = [power, power]
            meter["phase_edge_j"] = sum(meter["edge_powers_w"]) * (meter["r_max_s"] + meter["sample_interval_s"])
            meter["offset_bound_w"] = max(meter["edge_powers_w"]) * (meter["r_max_s"] + meter["sample_interval_s"]) / r["duration_s"]
            # The fixture's outside waveform is exactly the encoded 0.2 W.
            # Equality here identifies that payload value, not an agreement bar.
            before = [w if w == .2 else power for w in meter["adjacent_before_edge_powers_w"]]
            meter["adjacent_before_edge_powers_w"] = before
            meter["offset_sensitivity_w"] = before[0] - before[1]
            out.append(dict(r, rails_j=e, rails_secondary_j=e - idle_rails, meter=meter))
        return out


    def sel(points):
        return [p for p in points if p["selection"] == "primary" and p["basis"] == "gross primary"]


    for world in ("bytes", "time", "resident"):
        rng = random.Random({"bytes": 11, "time": 22, "resident": 33}[world])
        est = {}
        for rep in range(R):
            rec = redraw(world, rng)
            passes = ba.reduce_models(rec, manifest)
            points = sel(ba.combine_passes(passes))
            rails = {p["model"]: p["power"] for p in points if p["boundary"] == "rails"}
            for boundary in ba.BOUNDARIES:
                sub = [p for p in points if p["boundary"] == boundary]
                out = ba.h2(sub, rails)
                for fit in ("two_term", "resident_extended"):
                    f = out[fit]
                    for method, covariance in (("HC3", "covariance"), ("OLS", "ols_covariance")):
                        se = math.sqrt(f[covariance][1][1])
                        est.setdefault((boundary, fit, method), []).append((f["coefficients"][1], se, f["df"],
                            f["coefficient_C"][1] if boundary != "rails" else 0.0))
        for (boundary, fit, method), rows in est.items():
            factor = 2 if boundary == "DC input" else 1
            truth = population_eps(world, factor) if fit == "two_term" else (.01 * factor if world == "bytes" else 0.0)
            eps = [r[0] for r in rows]
            sd = statistics.stdev(eps)
            se = statistics.fmean(r[1] for r in rows)
            df = rows[0][2]
            k_spec = 11 if boundary == "rest" else 9
            ts, t95 = tq(1 - .05 / (2 * k_spec), df), tq(.975, df)
            cov = lambda t, offset=False: sum(abs(e - truth) <= t * s + (c if offset else 0)
                                               for e, s, _, c in rows) / len(rows)
            report.append({"world": world, "boundary": boundary, "fit": fit, "method": method,
                "draws": R, "truth": truth, "sd": sd, "mean_se": se, "se_over_sd": se / sd,
                "plain_95": cov(t95), "ruled_k": cov(ts), "k": k_spec,
                "offset_plain_95": cov(t95, True) if boundary != "rails" else None,
                "offset_ruled_k": cov(ts, True) if boundary != "rails" else None})
    return report


if __name__ == "__main__":
    print(json.dumps(run(Path(sys.argv[1]), int(sys.argv[2]) if len(sys.argv)>2 else 400), sort_keys=True))
