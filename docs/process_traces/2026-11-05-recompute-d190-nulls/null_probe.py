"""Synthetic n=1 estimator-field probe, separate from full-window S10 acceptance."""
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tests.independent_recompute.support import full_pack, run_cli
from tests.independent_recompute.test_comparator import cmp, DECODE, PREFILL
from tests.b5_analysis.test_step11_null_outcomes import NotEstimable


with tempfile.TemporaryDirectory(prefix="d190-n1-") as tmp:
    root = Path(tmp)
    archives = {pack: full_pack(root, pack, n=1 if pack == "GAMMA" else 5)
                for pack in ("ALPHA", "BETA", "GAMMA")}
    rc, output, _ = run_cli(archives, root / "recompute.json")
    assert rc == 0

c = cmp.Comparison(cmp.load_bars(cmp.DEFAULT_BARS))
for release in NotEstimable().primary["contrasts"]:
    cid = DECODE if release["contrast_id"] == "decode" else PREFILL
    own = output["contrasts"][cid]
    reasons = (cmp.estimator_null_reason(release), cmp.estimator_null_reason(own, independent=True))
    est, bounds, mult = (release[k] for k in ("estimator", "deterministic_bounds", "multiplicity"))
    fields = [("contrast_j", key, est[source], own[key]) for key, source in
              (("dbar_j", "estimate"), ("s_d_j", "s_d"), ("se_j", "SE_total"))]
    fields += [("contrast_p", "t_critical", est["t_critical_95"], own["t_star"]),
               ("contrast_j", "D_j", bounds["total"], own["D_j"]),
               ("contrast_j", "D_terms_j", cmp.terms_total(bounds["terms"]), own["D_j"]),
               ("contrast_p", "raw_p", mult["raw_p"], own["p"]),
               ("contrast_p", "adjusted_p", mult["adjusted_p"], own["holm_p"]),
               ("count", "df", est["df"], own["df"])]
    for name, source in (("metrology_interval_j", est["metrology_aware_CI95"]),
                         ("decision_interval_j", bounds["decision_interval"])):
        fields += [("contrast_j", name + "/" + side, a, b) for side, a, b in cmp.sides(source, own[name])]
    for family, key, a, b in fields:
        c.numeric(family, cid + "/" + key, a, b, null_reasons=reasons)

summary = dict(case="n1_registered_estimator_fields", synthetic_only=True,
    scope="26 estimator fields only; no full-window routing or step-11 coverage assessment",
    comparisons=len(c.rows), numeric_agreements=sum("difference" in r and r["verdict"] == "AGREE" for r in c.rows),
    agree_null=c.null_counts(), disagreements=sum(r["verdict"] != "AGREE" for r in c.rows),
    uncovered=None, unmapped=None)
assert summary["comparisons"] == summary["agree_null"]["total"] == 26
assert summary["disagreements"] == 0
Path(sys.argv[1]).write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n")
print(json.dumps(summary))
