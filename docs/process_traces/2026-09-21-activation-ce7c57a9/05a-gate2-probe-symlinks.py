import json, os, sys, time
from pathlib import Path
sys.path.insert(0, os.getcwd())
from joulewise import evidence_night as e
F = Path(sys.argv[1]); C = F/"roots"/"night-custody"
head = "0"*40
def plan(root, t0=None):
    t0 = (int(time.time())//60 - 60*24*10)*60 if t0 is None else t0
    return dict(schema="joulewise.night_plan.v2", schema_version=2, plan_id=root.name,
        receipt_class="DIAGNOSTIC_NO_PACK", t0_epoch_s=float(t0), window_max_s=9000,
        authored_epoch_s=float(t0-3600), repo_head=head, chain_path="chain.zsh",
        chain_sha256_path="chain.zsh.sha256", custody_root=str(root), measurement_head=head,
        measurement_root=str(F), registration_path="docs/registration.md")
def mk(name, marker=True):
    r = C/name; (r/"night").mkdir(parents=True)
    if marker: (r/"night"/"courier.sent").write_text("{}")
    (r/"night_plan.json").write_text(json.dumps(plan(r))); return r
def run(label):
    try:
        out = e.retained_roots({"roots_under": str(F/"roots")})
        print(label, "->", [(Path(r["plan"]).parent.name, r["classification"]) for r in out["inventory"]], "verdict", out["verdict"])
    except e.Refused as exc:
        print(label, "-> Refused:", exc)
    for p in C.iterdir():
        import shutil; shutil.rmtree(p) if not p.is_symlink() else p.unlink()
r = mk("S"); (r/"night"/"stray").symlink_to("/etc/hosts"); (r/"unrelated").symlink_to("/etc/hosts"); (r/"scratch").mkdir(); (r/"scratch"/"x").symlink_to("/etc/hosts")
run("S unrelated symlinks night/stray, <root>/unrelated, <root>/scratch/x")
r = mk("W", marker=False); (r/"night"/"courier.sent").symlink_to("/etc/hosts")
run("W night/courier.sent is a symlink")
r = mk("N"); real = F/"realnight"; (r/"night").rename(real); (r/"night").symlink_to(real)
run("N night/ is a symlink")
r = mk("K"); (r/"night_plan.json").unlink(); (r/"night_plan.json").symlink_to("/etc/hosts")
run("K night_plan.json is a symlink")
real = F/"realroot"; r = mk("Z"); r.rename(real); (C/"Z").symlink_to(real)
run("Z the root directory itself is a symlink (ancestor of the plan)")
r = mk("R7", marker=False); (r/"night"/"refusal-7.json").write_text("{}"); (r/"night"/"result.json").symlink_to("/etc/hosts")
run("R7 refusal-7.json regular + result.json symlink")
r = mk("Q"); (r/"night"/"refusal-02.json").symlink_to("/etc/hosts")
run("Q refusal-02.json is a symlink (refusal-glob hit)")
