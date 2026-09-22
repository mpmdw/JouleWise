"""Exhibit A generator: verbatim function/class extracts from `git show <rev>:<path>` located by ast; prints with line numbers."""
import ast, subprocess, sys
rev = sys.argv[1]
WANT = [
 ("joulewise/quiet_predicate_campaign.py", ["frozen_protocol","validate_protocol","process_groups","cleanup_groups","hard_exclusions","pilot_summary","execute"]),
 ("scripts/run_night.py", ["_group_census"]),
 ("scripts/sample_quiet_predicate_evidence.py", ["PowerRecorder","align_frames","integrate","reduce_interior","collect"]),
 ("joulewise/night_gate.py", ["RULED_REGISTRATIONS"]),
]
print(f"# Exhibit A — code at main `{rev}` (verbatim `git show {rev}:<path>` extracts located by `ast`, printed with 1-based line numbers)\n")
for path, names in WANT:
    src = subprocess.run(["git","show",f"{rev}:{path}"],capture_output=True,text=True,check=True).stdout
    lines = src.splitlines()
    tree = ast.parse(src)
    spans = {}
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and node.name in names:
            spans.setdefault(node.name,(node.lineno,node.end_lineno))
        if isinstance(node,ast.Assign):
            for t in node.targets:
                if isinstance(t,ast.Name) and t.id in names:
                    spans.setdefault(t.id,(node.lineno,node.end_lineno))
    for name in names:
        if name not in spans:
            print(f"## A — `{path}` `{name}`: NOT FOUND at {rev}\n"); continue
        a,b = spans[name]
        print(f"## A — `{path}:{a}-{b}` `{name}`\n\n```python")
        for i in range(a,b+1): print(f"{i:5d}  {lines[i-1]}")
        print("```\n")
