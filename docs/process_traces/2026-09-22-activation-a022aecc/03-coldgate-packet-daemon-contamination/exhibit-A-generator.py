"""Exhibit A generator: verbatim `git show <rev>:<path>` extracts located by `ast`, printed with 1-based line numbers.

Run from the worktree root:  python3 exhibit-A-generator.py 91f80870 > exhibit-A-code-at-main.md
"""
import ast, hashlib, json, subprocess, sys

rev = sys.argv[1]
_cache = {}


def show(path):
    if path not in _cache:
        _cache[path] = subprocess.run(["git", "show", f"{rev}:{path}"],
                                      capture_output=True, text=True, check=True).stdout
    return _cache[path]


def block(path, a, b, label, lang="python"):
    lines = show(path).splitlines()
    a = max(1, a)
    b = min(len(lines), b)
    print(f"### {label} — `{path}:{a}-{b}`\n\n```{lang}")
    for i in range(a, b + 1):
        print(f"{i:5d}  {lines[i-1]}")
    print("```\n")


def spans(path):
    """name -> (lineno, end_lineno) for defs, classes and module-level assignments."""
    tree = ast.parse(show(path))
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.setdefault(node.name, (node.lineno, node.end_lineno))
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    out.setdefault(t.id, (node.lineno, node.end_lineno))
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            out.setdefault(node.target.id, (node.lineno, node.end_lineno))
    return out


def by_name(path, name, label):
    sp = spans(path)
    if name not in sp:
        print(f"### {label} — `{path}` `{name}`: NOT FOUND at {rev}\n")
        return
    a, b = sp[name]
    block(path, a, b, f"{label} `{name}`")


def enclosing(path, lineno):
    """Innermost function/class whose span contains lineno, else '<module>'."""
    tree = ast.parse(show(path))
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.lineno <= lineno <= node.end_lineno:
                if best is None or node.lineno > best.lineno:
                    best = node
    return best


def by_text(path, needle, label, before=0, after=0, whole=False):
    lines = show(path).splitlines()
    hits = [i + 1 for i, l in enumerate(lines) if needle in l]
    if not hits:
        print(f"### {label} — `{path}`: text {needle!r} NOT FOUND at {rev}\n")
        return
    for h in hits:
        node = enclosing(path, h)
        who = f"`{node.name}`" if node is not None else "`<module>`"
        if whole and node is not None:
            print(f"_{label}: hit at line {h}; enclosing function {who} (lines {node.lineno}-{node.end_lineno}), shown whole._\n")
            block(path, node.lineno, node.end_lineno, f"{label} {who}")
        else:
            print(f"_{label}: hit at line {h}; enclosing function {who}._\n")
            block(path, h - before, h + after, f"{label} (hit line {h}, enclosing {who})")


print(f"# Exhibit A — code at main `{rev}`\n")
print(f"Every block below is the verbatim output of `git show {rev}:<path>`, located by `ast` "
      "(function/class/assignment spans) or by exact text match, printed with 1-based line numbers. "
      "Nothing is read from the working tree.\n")

print("## A1 — `joulewise/night_gate.py`: load predicate, reason codes, decision-record fields, `_check_machine`, hard-gate call site\n")
by_name("joulewise/night_gate.py", "LOAD_AVG_ARGV", "A1a load probe constant")
by_name("joulewise/night_gate.py", "LOAD_MAX", "A1b load ceiling")
block("joulewise/night_gate.py", 137, 154, "A1c constants block in context (agent census argv through LOAD_MAX)")
by_name("joulewise/night_gate.py", "NIGHT_GATE_REASON_CODES", "A1d gate reason codes")
by_name("joulewise/night_gate.py", "_QUIET_RECEIPT_KEYS", "A1e decision-record field set (contains `top_consumers_at_decision`, `load_avg_diagnostic`)")
by_name("joulewise/night_gate.py", "_check_machine", "A1f")
by_text("joulewise/night_gate.py", "legacy_load=False", "A1g hard-gate call site", before=8, after=6)

print("## A2 — `joulewise/quiet_admission.py`: the driver-side quiet predicate\n")
by_name("joulewise/quiet_admission.py", "is_quiet", "A2a")
by_name("joulewise/quiet_admission.py", "validate_policy", "A2b")
by_text("joulewise/quiet_admission.py", "top_consumers=sorted(consumers", "A2c top_consumers builder", whole=True)

print("## A3 — `joulewise/quiet_predicate_campaign.py`: covariates, stop branch, sizing, pilot summary, attestation exclusions\n")
for n, lbl in (("record_covariates", "A3a"), ("stop_branch", "A3b"), ("size_block_two", "A3c"),
               ("pilot_summary", "A3d"), ("attestation_exclusions", "A3e"), ("hard_exclusions", "A3f"),
               ("chi_square_lower_decile", "A3g")):
    by_name("joulewise/quiet_predicate_campaign.py", n, lbl)

print("## A4 — `joulewise/evidence_night.py`: the arm-notice text that states the busy-cores role\n")
by_text("joulewise/evidence_night.py", "Busy cores remain a descriptive covariate",
        "A4 notice text", before=15, after=15)

print("## A5 — `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v2.json` (complete) and its digest\n")
P = "configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v2.json"
raw = subprocess.run(["git", "show", f"{rev}:{P}"], capture_output=True, check=True).stdout
file_sha = hashlib.sha256(raw).hexdigest()
ng = show("joulewise/night_gate.py")
pinned = None
for line in ng.splitlines():
    if line.startswith("QPE01_PILOT_REGISTRATION_SHA256"):
        pinned = line.split("=", 1)[1].strip().strip('"')
print("```")
print(f"sha256(git show {rev}:{P}) = {file_sha}")
print(f"night_gate.QPE01_PILOT_REGISTRATION_SHA256 = {pinned}")
print(f"MATCH = {file_sha == pinned}")
print("```\n")
block(P, 1, len(raw.decode().splitlines()), "A5 registration (complete)", lang="json")

print("## A6 — agent census argv and the foreign-pid classifier\n")
by_name("joulewise/night_gate.py", "AGENT_CENSUS_ARGV", "A6a")
by_name("joulewise/night_gate.py", "agent_census", "A6b")
by_name("joulewise/arm_census.py", "classify_arm_census", "A6c")
