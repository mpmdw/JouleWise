"""Exhibit C generator — executed evidence, re-run at assembly time.

Cheap read-only probes are RE-EXECUTED here so exhibit C is generator output
rather than a copy of a record: the estimator-pin digests at the final feature
head, the acceptance artifacts' derivation-digest recomputation through the
production `_canonical_sha256`, the header-guard evaluation over the three
saved log bodies, and the scratch/feature path-overlap check.  Expensive runs
(test suites, corpus replay, the quick tier, the corpus verify script) are NOT
re-run; their tails are quoted verbatim in section C6 and labelled with the
record step that executed them.

    python3 exhibit-C-generator.py [repo_path] > exhibit-C-executed-evidence.md

No argument is a revision: every revision is hard-pinned below.
"""
import ast
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
FEATURE_REV = "489b0953"
SCRATCH_BASE = "447fd6bf"
SCRATCH_HEAD = "e52c7fbc"
MAIN_REV = "c8812172"
QC = "joulewise/quiet_predicate_campaign.py"
R6 = "configs/calibration/calibration_acceptance_d079_v2_n17_r6.json"
R7 = "configs/calibration/calibration_acceptance_d079_v2_n17_r7.json"
FIXTURE = "tests/fixtures/qpe01_pilot_n1_20260922/exhibit-D-timed-log.txt"
TRACE = "docs/process_traces/2026-09-22-activation-59857fe5"
D2 = f"{TRACE}/07c-exhibit-D2-timed-log-0210-0435-syslog.txt"
D3 = f"{TRACE}/07c-exhibit-D3-timed-log-zero-match-syslog.txt"
PROPOSED_SYSLOG_HEADER = "Timestamp                       (process)[PID]"


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args],
                          capture_output=True, text=True, check=True).stdout


def sha(data):
    return hashlib.sha256(data).hexdigest()


print("# Exhibit C — executed evidence (generator output, verbatim)\n")
print(f"Generated {time.strftime('%Y-%m-%d %H:%M:%S %Z')} against repository "
      f"`{REPO}`. Revisions: feature head `{FEATURE_REV}`, scratch "
      f"`{SCRATCH_BASE}..{SCRATCH_HEAD}`, main `{MAIN_REV}`. Everything in C1–C5 was "
      "executed by this generator; C6 is quoted, not re-run.\n")

# ------------------------------------------------------------------ C1
print("## C1 — the four D-138 governed estimator files at the FINAL feature head "
      "vs the r7 candidate's pins\n")
print("Re-executes record 01 step 8 at `489b0953` (the step was executed at `c5f4f9c6`, "
      "before the fix round's 15 commits). `pinned` is read out of the r7 artifact at "
      f"`{SCRATCH_HEAD}`; `observed` is `sha256(git show {FEATURE_REV}:<path>)`.\n")
r7_doc = json.loads(git("show", f"{SCRATCH_HEAD}:{R7}"))
r6_doc = json.loads(git("show", f"{SCRATCH_HEAD}:{R6}"))
pins = r7_doc["prospective_rederivation"]["estimator_code_sha256"]
r6_pins = r6_doc["prospective_rederivation"]["estimator_code_sha256"]
print("```")
print(f"r7 acceptance_id: {r7_doc['acceptance_id']}")
print(f"r6 acceptance_id: {r6_doc['acceptance_id']}")
for path in sorted(pins):
    observed = sha(subprocess.run(["git", "-C", str(REPO), "show", f"{FEATURE_REV}:{path}"],
                                  capture_output=True, check=True).stdout)
    verdict = "MATCH" if observed == pins[path] else "MISMATCH"
    moved = "moved r6->r7" if r6_pins.get(path) != pins[path] else "unchanged r6->r7"
    print(f"{verdict:9s} {path}")
    print(f"          pinned   {pins[path]}  ({moved})")
    print(f"          observed {observed}")
print("```\n")

# ------------------------------------------------------------------ C2
print("## C2 — derivation-digest recomputation through the production helper\n")
sys.path.insert(0, str(REPO))
from joulewise import calibration_bracketing  # noqa: E402

helper_path = Path(calibration_bracketing.__file__)
print(f"Imported `joulewise.calibration_bracketing` from `{helper_path}` "
      f"(sha256 `{sha(helper_path.read_bytes())}`). The core is every key except "
      "`derivation_sha256`, exactly as the production validator builds it "
      "(`calibration_bracketing.py:680`).\n")
print("```")
for label, doc in (("r6", r6_doc), ("r7", r7_doc)):
    core = {key: item for key, item in doc.items() if key != "derivation_sha256"}
    recomputed = calibration_bracketing._canonical_sha256(core)
    stored = doc["derivation_sha256"]
    print(f"{label}: stored      {stored}")
    print(f"{label}: recomputed  {recomputed}   "
          f"{'MATCH' if stored == recomputed else 'MISMATCH'}")
print("```\n")

# ------------------------------------------------------------------ C3
print("## C3 — the header guard at `489b0953` over the three saved log bodies\n")
qc_source = git("show", f"{FEATURE_REV}:{QC}")
qc_lines = qc_source.splitlines()
wanted = {"TIMED_LOG_HEADER_FIELDS", "TIMED_LOG_MARKERS", "timed_log_has_header",
          "timed_log_marker_lines"}
found = {}
for node in ast.walk(ast.parse(qc_source)):
    if isinstance(node, ast.FunctionDef) and node.name in wanted:
        found.setdefault(node.name, (node.lineno, node.end_lineno))
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in wanted:
                found.setdefault(target.id, (node.lineno, node.end_lineno))
namespace = {}
extracted = []
for name in ("TIMED_LOG_HEADER_FIELDS", "TIMED_LOG_MARKERS",
             "timed_log_has_header", "timed_log_marker_lines"):
    first, last = found[name]
    text = "\n".join(qc_lines[first - 1:last])
    extracted.append(f"# {QC}:{first}-{last} at {FEATURE_REV}\n{text}")
    exec(compile(text, f"{QC}@{FEATURE_REV}", "exec"), namespace)
print("The four definitions below are extracted by `ast` from "
      f"`git show {FEATURE_REV}:{QC}` and executed as-is; nothing else from the module "
      "is loaded.\n")
print("```python")
print("\n\n".join(extracted))
print("```\n")

bodies = {}
bodies["exhibit D (fixture, compact style)"] = (
    FIXTURE, subprocess.run(["git", "-C", str(REPO), "show", f"{FEATURE_REV}:{FIXTURE}"],
                            capture_output=True, check=True).stdout)
bodies["exhibit D2 (live syslog, 02:10-04:35 window)"] = (D2, (REPO / D2).read_bytes())
bodies["exhibit D3 (live syslog, zero-match)"] = (D3, (REPO / D3).read_bytes())
print("```")
for label, (path, raw) in bodies.items():
    text = raw.decode("utf-8")
    lines = text.splitlines()
    print(f"{label}")
    print(f"  path      {path}")
    print(f"  sha256    {sha(raw)}")
    print(f"  bytes     {len(raw)}   lines {len(lines)}")
    print(f"  line[0]   {lines[0]!r}" if lines else "  line[0]   <no lines>")
    print(f"  timed_log_has_header(text)   = {namespace['timed_log_has_header'](text)}")
    print(f"  timed_log_marker_lines(text) = {namespace['timed_log_marker_lines'](text)}")
    print(f"  line[0].rstrip() == proposed syslog header constant: "
          f"{bool(lines) and lines[0].rstrip() == PROPOSED_SYSLOG_HEADER}")
print("```\n")

print("### C3b — the lead's proposed Q2 guard evaluated over the same corpus\n")
print("Proposed guard (lead's Q2 option (a)): the body's first line, right-stripped, "
      f"equals the frozen constant `{PROPOSED_SYSLOG_HEADER!r}`. Evaluated here against "
      "the three saved bodies and against the four counterfactual bodies the lead's "
      "regression names. `entry line` is taken mechanically as exhibit D2's SECOND "
      "line, so it is a real headerless body, not a hand-written one.\n")


def proposed_guard(text):
    first = text.splitlines()[0] if text else ""
    return first.rstrip() == PROPOSED_SYSLOG_HEADER


d2_text = bodies["exhibit D2 (live syslog, 02:10-04:35 window)"][1].decode("utf-8")
d_text = bodies["exhibit D (fixture, compact style)"][1].decode("utf-8")
d3_text = bodies["exhibit D3 (live syslog, zero-match)"][1].decode("utf-8")
cases = [
    ("D2 full body (live syslog, non-empty)", d2_text),
    ("D3 full body (live syslog, zero match, header only)", d3_text),
    ("D full body (compact-style fixture)", d_text),
    ("empty body", ""),
    ("html error page", "<html>error</html>"),
    ("bare newline", "\n"),
    ("headerless entry line (D2 line 2 onward)", "\n".join(d2_text.splitlines()[1:])),
    ("compact header line alone", d_text.splitlines()[0]),
]
print("```")
for label, text in cases:
    print(f"{str(proposed_guard(text)):5s}  proposed_guard  | "
          f"{str(namespace['timed_log_has_header'](text)):5s}  guard at {FEATURE_REV}  "
          f"| {label}")
print("```\n")

# ------------------------------------------------------------------ C4
print("## C4 — revision topology and the scratch/feature path-overlap check\n")
print("```")
for label, rev in (("feature head", FEATURE_REV), ("scratch head", SCRATCH_HEAD),
                   ("scratch base / feature base", SCRATCH_BASE), ("main", MAIN_REV)):
    print(f"{label:27s} {git('rev-parse', rev).strip()}")
for child, parent in ((FEATURE_REV, SCRATCH_BASE), (SCRATCH_HEAD, SCRATCH_BASE)):
    ancestor = subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor",
                               parent, child]).returncode == 0
    print(f"{parent} is ancestor of {child}: {ancestor}")
feature_paths = set(git("diff", "--name-only", f"{SCRATCH_BASE}..{FEATURE_REV}").split())
scratch_paths = set(git("diff", "--name-only", f"{SCRATCH_BASE}..{SCRATCH_HEAD}").split())
print(f"\nfeature delta {SCRATCH_BASE}..{FEATURE_REV}: {len(feature_paths)} paths")
for path in sorted(feature_paths):
    print(f"  F  {path}")
print(f"scratch delta {SCRATCH_BASE}..{SCRATCH_HEAD}: {len(scratch_paths)} paths")
for path in sorted(scratch_paths):
    print(f"  S  {path}")
print(f"\nintersection: {sorted(feature_paths & scratch_paths) or 'EMPTY'}")
print("```\n")

# ------------------------------------------------------------------ C5
print("## C5 — the r7 candidate's registry pin vs its own bytes\n")
print("The scratch head registers r7 in `ISSUED_ACCEPTANCE_REGISTRY` with a "
      "`file_sha256`. That pin is compared here against the artifact's bytes at the "
      "same revision.\n")
registry_source = git("show", f"{SCRATCH_HEAD}:joulewise/calibration_bracketing.py")
pin = None
for node in ast.walk(ast.parse(registry_source)):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if (isinstance(target, ast.Name)
                    and target.id == "ANCHOR_V3_R7_ACCEPTANCE_BOUND_SHA256"):
                pin = ast.literal_eval(node.value)
r7_bytes = subprocess.run(["git", "-C", str(REPO), "show", f"{SCRATCH_HEAD}:{R7}"],
                          capture_output=True, check=True).stdout
print("```")
print(f"ANCHOR_V3_R7_ACCEPTANCE_BOUND_SHA256 = {pin}")
print(f"sha256(git show {SCRATCH_HEAD}:{R7})  = {sha(r7_bytes)}")
print(f"verdict: {'MATCH' if pin == sha(r7_bytes) else 'MISMATCH'}")
print(f"r6 bytes sha256                        = "
      f"{sha(subprocess.run(['git', '-C', str(REPO), 'show', f'{SCRATCH_HEAD}:{R6}'], capture_output=True, check=True).stdout)}")
print("```\n")

# ------------------------------------------------------------------ C6
print("## C6 — expensive runs: NOT re-executed, quoted verbatim from record 01\n")
print("Each block below is a verbatim quotation from "
      f"`{TRACE}/01-launch-and-resume-record.md` at the bookkeeping head, labelled "
      "with the step that executed it. The generator does not re-run these.\n")
QUOTES = [
    ("record 01 step 9, magistrate-executed — neutrality proof part 1 "
     "(`tests/verify_calibration_acceptance_corpus.py`)",
     "r7 → `n=17 min=0.02317490442656863 (20260722T215127-eeef661a) "
     "max=0.03289849371536248 (20260722T214220-1acdbbc0) range=0.00972358928879385 "
     "mean=0.026848579671140323 sample_sd=0.002460856207694636 … "
     "PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK`; r6 under the same command prints the "
     "identical five statistics and `OK`."),
    ("record 01 step 11, magistrate-executed — the six D-138-affected calibration "
     "modules on the scratch branch",
     "`Ran 349 tests in 546.361s OK (skipped=5)`"),
    ("record 01 step 12, magistrate-executed — quick tier on the scratch head "
     "`e52c7fbc`",
     "`modules=153 excluded=92 failures=0 seconds=72.139 result=PASS`"),
    ("record 01 step 18, magistrate-executed — corpus replay at `62412ee6` vs "
     "`corpus-v3-baseline-9b6b3f0e.json` (38 members)",
     "**EQUAL 38, DIFF 0, NOT_EXECUTED 0** (v3 dict AND raw sha256 equal per member)"),
    ("record 01 step 14, seat-executed and magistrate-verified — the three brief-06 "
     "modules at the fix head",
     "`Ran 224 tests in 55.218s OK` (177 before)"),
    ("record 01 step 22, magistrate-executed — the full seven-module exit-contract run "
     "at `62412ee6`, INCLUDING its one failure",
     "`Ran 616 tests in 884.637s FAILED (failures=1)` — "
     "`tests.test_run_night.WindowDeadlineTests."
     "test_a_grandchild_that_ignores_sigterm_is_killed_and_still_proven`. The record "
     "classifies it a contention flake rather than a delta defect: the three files it "
     "exercises are untouched by the fix round, the test alone re-ran "
     "`Ran 1 test in 7.340s OK`, and the whole module alone `Ran 228 tests in 108.994s "
     "OK`. The seat's own run of the same four modules was `Ran 392 tests in 742.268s "
     "OK` and the `c5f4f9c6` baseline `569 OK`."),
    ("record 01 step 20, execution-lens-executed — byte invariance of a no-failure "
     "night between `c5f4f9c6` and `62412ee6`",
     "`evidence_outcome.json`: zero differences; the only differences anywhere are the "
     "two additive keys (`network_time_attestation_wall_s`, `window_argv_epoch_s`) plus "
     "`summary.whole_campaign_observer_cpu_s`, which is the measured CPU of the test "
     "process."),
]
for label, text in QUOTES:
    print(f"**{label}**\n\n> {text}\n")
print("Note on scope: steps 14, 18 and 20 were executed at `62412ee6`. The feature head "
      f"`{FEATURE_REV}` is one further commit whose entire diff is inside the "
      "`record_attestation` docstring (record 01 step 19). The generator does not "
      "re-run them; the diff `62412ee6..489b0953` is printed here so the judge can size "
      "that gap itself.\n")
print("```diff")
print(git("diff", f"62412ee6..{FEATURE_REV}").rstrip())
print("```")
