"""Exhibit A generator — verbatim code and diff extracts at pinned revisions.

Every extract is produced by `git show <rev>:<path>` and located by `ast`
(function/class/assignment spans) or by a PRINTED anchor string, never by a
hand-copied line range.  Run from any checkout of this repository:

    python3 exhibit-A-generator.py [repo_path] > exhibit-A-code-at-revisions.md

Revisions are hard-pinned below; the generator takes no revision arguments.
"""
import ast
import json
import subprocess
import sys

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
FEATURE_REV = "489b0953"          # feat/2026-09-22-a267-clock-anchor-v3_1 head
SCRATCH_BASE = "447fd6bf"         # origin base of the r7 dry-run scratch branch
SCRATCH_HEAD = "e52c7fbc"         # scratch/r7-dryrun-e4b4ead6 head
QC = "joulewise/quiet_predicate_campaign.py"
SQ = "scripts/sample_quiet_predicate_evidence.py"
R6 = "configs/calibration/calibration_acceptance_d079_v2_n17_r6.json"
R7 = "configs/calibration/calibration_acceptance_d079_v2_n17_r7.json"


def git(*args):
    return subprocess.run(["git", "-C", REPO, *args],
                          capture_output=True, text=True, check=True).stdout


def show(rev, path):
    return git("show", f"{rev}:{path}")


def spans(source, names):
    """Map name -> (first_line, last_line) from one ast walk."""
    found = {}
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name in names:
                found.setdefault(node.name, (node.lineno, node.end_lineno))
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    found.setdefault(target.id, (node.lineno, node.end_lineno))
    return found


def with_leading_comment(lines, first):
    """Extend a span upward over the contiguous comment block above it."""
    index = first - 1                      # 0-based index of the first line
    while index - 1 >= 0 and lines[index - 1].lstrip().startswith("#"):
        index -= 1
    return index + 1


def emit(path, rev, lines, first, last, label, note=""):
    print(f"## A — `{path}:{first}-{last}` at `{rev}` — {label}")
    if note:
        print(f"\n{note}")
    print("\n```python")
    for number in range(first, last + 1):
        print(f"{number:5d}  {lines[number - 1]}")
    print("```\n")


def anchor_index(lines, first, last, needle):
    """1-based line number of the single line in [first,last] holding needle."""
    hits = [n for n in range(first, last + 1) if needle in lines[n - 1]]
    if len(hits) != 1:
        raise SystemExit(f"anchor {needle!r} matched {len(hits)} lines in "
                         f"[{first},{last}] — generator refuses to guess")
    return hits[0]


def flatten(value, prefix=""):
    """Recursive field flattening: dotted/bracketed path -> JSON scalar text."""
    if isinstance(value, dict):
        out = {}
        for key in value:
            out.update(flatten(value[key], f"{prefix}.{key}" if prefix else str(key)))
        return out
    if isinstance(value, list):
        out = {}
        for index, item in enumerate(value):
            out.update(flatten(item, f"{prefix}[{index}]"))
        return out
    return {prefix: json.dumps(value)}


print("# Exhibit A — code and diff at the pinned revisions "
      f"(feature head `{FEATURE_REV}`, scratch `{SCRATCH_BASE}..{SCRATCH_HEAD}`)\n")
print("Generator output. Every extract below is `git show <rev>:<path>` located by "
      "`ast` or by the printed anchor string, with 1-based line numbers of the file "
      "at that revision. Nothing is paraphrased and nothing is hand-trimmed.\n")

# ---------------------------------------------------------------- A1..A11
qc_source = show(FEATURE_REV, QC)
qc_lines = qc_source.splitlines()
qc_names = ["TIMED_LOG_MARKERS", "TIMED_LOG_PREDICATE", "TIMED_LOG_HEADER_FIELDS",
            "ATTESTATION_TIMEOUT_FLOOR_S", "CLEANUP_BUDGET_RESERVE_S",
            "timed_log_argv", "timed_log_has_header", "timed_log_window_epoch_s",
            "attestation_timeout_s", "attest_network_time", "record_attestation",
            "restore_network_time", "cleanup_budget_s", "execute"]
qc_spans = spans(qc_source, qc_names)
missing = [name for name in qc_names if name not in qc_spans]
if missing:
    raise SystemExit(f"NOT FOUND at {FEATURE_REV}: {missing}")

print("### Module constants (each with the contiguous comment block above it)\n")
for name in ("TIMED_LOG_MARKERS", "TIMED_LOG_PREDICATE", "TIMED_LOG_HEADER_FIELDS",
             "ATTESTATION_TIMEOUT_FLOOR_S", "CLEANUP_BUDGET_RESERVE_S"):
    first, last = qc_spans[name]
    emit(QC, FEATURE_REV, qc_lines, with_leading_comment(qc_lines, first), last, f"`{name}`")

print("### Functions\n")
for name in ("timed_log_argv", "timed_log_has_header", "timed_log_window_epoch_s",
             "attestation_timeout_s", "attest_network_time", "record_attestation",
             "restore_network_time", "cleanup_budget_s"):
    first, last = qc_spans[name]
    emit(QC, FEATURE_REV, qc_lines, first, last, f"`{name}`")

print("### Two sections of `execute`\n")
execute_first, execute_last = qc_spans["execute"]
attest_line = anchor_index(qc_lines, execute_first, execute_last,
                           "attestation_began = time.monotonic()")
journal_line = anchor_index(qc_lines, attest_line, execute_last,
                            'append_event(night_dir / "evidence_envelopes.jsonl"')
emit(QC, FEATURE_REV, qc_lines,
     with_leading_comment(qc_lines, attest_line), journal_line,
     f"`execute` inter-slot section",
     note=f"Anchors: first line = the contiguous comment block above the single line "
          f"holding `attestation_began = time.monotonic()` ({attest_line}); last line = "
          f"the single line at or after {attest_line} holding "
          f"`append_event(night_dir / \"evidence_envelopes.jsonl\"` ({journal_line}; the other "
          f"match in `execute` is the A269 Q3 start-drift abort event, before this point). "
          f"`execute` spans {execute_first}-{execute_last}.")
base_line = anchor_index(qc_lines, execute_first, execute_last, "base = 0 if outcome in")
emit(QC, FEATURE_REV, qc_lines,
     with_leading_comment(qc_lines, base_line), execute_last,
     "`execute` return-code tail",
     note=f"Anchors: first line = the contiguous comment block above the single line "
          f"holding `base = 0 if outcome in` ({base_line}); last line = `execute`'s "
          f"`end_lineno` ({execute_last}).")

# ---------------------------------------------------------------- A12
print("### Collector: the integer-nanosecond window\n")
sq_source = show(FEATURE_REV, SQ)
sq_lines = sq_source.splitlines()
sq_spans = spans(sq_source, ["integrate", "integrate_seconds", "reduce_interior"])
for name in ("integrate_seconds", "integrate", "reduce_interior"):
    first, last = sq_spans[name]
    emit(SQ, FEATURE_REV, sq_lines, first, last, f"`{name}`")

# ---------------------------------------------------------------- A13
print("## A — r7 scratch delta: `git diff --stat "
      f"{SCRATCH_BASE}..{SCRATCH_HEAD}` and the commit list\n")
print("```")
print(git("diff", "--stat", f"{SCRATCH_BASE}..{SCRATCH_HEAD}").rstrip())
print(f"\ncommits {SCRATCH_BASE}..{SCRATCH_HEAD}:")
print(git("log", "--oneline", f"{SCRATCH_BASE}..{SCRATCH_HEAD}").rstrip())
print(f"commit count: {git('rev-list', '--count', f'{SCRATCH_BASE}..{SCRATCH_HEAD}').strip()}")
print("```\n")

print("## A — r7 scratch delta: full diff of `joulewise/arm_readiness.py`\n")
print("```diff")
print(git("diff", f"{SCRATCH_BASE}..{SCRATCH_HEAD}", "--", "joulewise/arm_readiness.py").rstrip())
print("```\n")

# ---------------------------------------------------------------- A14
print(f"## A — r6 → r7 acceptance artifact: recursive field diff at `{SCRATCH_HEAD}`\n")
print(f"Both artifacts are read with `git show {SCRATCH_HEAD}:<path>`, flattened to "
      "dotted/bracketed leaf paths, and compared leaf by leaf. Equal leaves are counted, "
      "not printed; every unequal, added or removed leaf is printed in full.\n")
r6 = json.loads(show(SCRATCH_HEAD, R6))
r7 = json.loads(show(SCRATCH_HEAD, R7))
flat6, flat7 = flatten(r6), flatten(r7)
only6 = sorted(set(flat6) - set(flat7))
only7 = sorted(set(flat7) - set(flat6))
differing = sorted(key for key in set(flat6) & set(flat7) if flat6[key] != flat7[key])
print("```")
print(f"r6 = {R6}")
print(f"r7 = {R7}")
print(f"leaf fields: r6 {len(flat6)}, r7 {len(flat7)}; "
      f"equal {len(set(flat6) & set(flat7)) - len(differing)}; "
      f"differing {len(differing)}; only-in-r6 {len(only6)}; only-in-r7 {len(only7)}")
for key in differing:
    print(f"\nDIFFERS  {key}\n    r6: {flat6[key]}\n    r7: {flat7[key]}")
for key in only6:
    print(f"\nONLY-r6  {key}: {flat6[key]}")
for key in only7:
    print(f"\nONLY-r7  {key}: {flat7[key]}")
print("```")
