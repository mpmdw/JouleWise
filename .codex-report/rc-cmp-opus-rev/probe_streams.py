"""RC-CMP-OPUS-REV probe: public streams (blinding) and run-time independence.

Builds test_auditfix's synthetic machine archive (raw 50 Hz KM003C stream), runs the
recompute CLI and the comparator CLI in subprocesses under an audit hook that logs
every import and every file open, and checks (a) stdout/stderr for any decimal
number other than the interpreter version, (b) any module or file under
joulewise/b5_analysis or joulewise/external touched by either script.
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tests.independent_recompute import test_auditfix, test_comparator as tc

HOOK = r'''
import sys, runpy
log = open(sys.argv[1], "w")
def hook(event, args):
    if event == "open" and isinstance(args[0], str):
        log.write("open " + args[0] + "\n")
    elif event == "import":
        log.write("import " + str(args[0]) + "\n")
    elif event in ("exec", "compile") and args and isinstance(args[0], str) and "joulewise" in args[0]:
        log.write(event + " " + args[0] + "\n")
sys.addaudithook(hook)
script, sys.argv = sys.argv[2], sys.argv[2:]
if len(sys.argv) > 1 and sys.argv[1] == "--raise-valued":
    sys.argv.pop(1)
    import importlib.util
    spec = importlib.util.spec_from_file_location("m", script); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    def boom(*a, **k): raise ValueError("energy 123.456 J p=0.0371")
    m.recompute = boom
    raise SystemExit(m.guarded_main(sys.argv[1:]))
runpy.run_path(script, run_name="__main__")
'''
tmp = Path(tempfile.mkdtemp())
hook = tmp / "hook.py"; hook.write_text(HOOK)
holder = type("Holder", (), {"root": tmp})()
archive, rid, recorded, _ = test_auditfix.AuditFixTests.machine_archive(holder)
NUM = re.compile(r"(?<![0-9a-f])[-+]?\d*\.\d+(e[-+]?\d+)?|\d+e[-+]?\d+", re.I)


def run(name, script, *args):
    log = tmp / (name + ".audit")
    p = subprocess.run([sys.executable, "-I", str(hook), str(log), str(ROOT / script), *args], capture_output=True, text=True)
    streams = p.stdout + p.stderr
    version = re.escape(".".join(map(str, sys.version_info[:3])))
    numbers = [m.group(0) for m in NUM.finditer(re.sub(r"python=" + version, "", streams))]
    touched = sorted({l for l in log.read_text().splitlines()
                      if re.search(r"joulewise[./](b5_analysis|external)", l)})
    print(f"{name}: exit={p.returncode} decimal_tokens_on_streams={numbers} l9_or_parser_touched={touched}")
    print("   stdout:", p.stdout.strip()[:400]); print("   stderr:", p.stderr.strip()[:200])
    return p


out = tmp / "recompute.json"
run("recompute", "scripts/independent_recompute_b5.py", "--alpha", str(archive), "--member-detail", "--out", str(out))
run("recompute-exception", "scripts/independent_recompute_b5.py", "--raise-valued", "--alpha", str(archive), "--out", str(tmp / "x.json"))

# Comparator on test_comparator's fixture (custody built as the unit test does).
case = tc.ComparatorTests("test_baseline_agrees_under_both_bar_sets"); case.setUp()
custody = case.custody(); ours = case.root / "ours.json"; ours.write_text(json.dumps(case.ours))
run("comparator", "scripts/compare_b5_recompute.py", "--l9-custody", str(custody), "--recompute", str(ours),
    "--restricted-out", str(tmp / "cmp.json"))
# NaN in an L9 restricted output (json.loads accepts NaN): the restricted write uses allow_nan=False.
case.files[f"outputs/{tc.SHA}-claim-verdicts.json"]["contrasts"][0]["estimator"]["estimate"] = float("nan")
custody = case.custody()
run("comparator-l9-nan", "scripts/compare_b5_recompute.py", "--l9-custody", str(custody), "--recompute", str(ours),
    "--restricted-out", str(tmp / "cmp-nan.json"))
print("restricted written for NaN case:", (tmp / "cmp-nan.json").exists())
