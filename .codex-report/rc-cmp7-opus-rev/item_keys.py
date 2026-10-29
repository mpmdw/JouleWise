import ast, sys, json
sys.path.insert(0, "scripts")
import compare_b5_recompute as cmp
src = open(sys.argv[1]).read()
tree = ast.parse(src)
allwords = {}
for sec, table in cmp.LINE_KEYS.items():
    for w, k in table.items():
        allwords.setdefault(w, []).append((sec, set(k)))
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "_item":
        if not node.args or not isinstance(node.args[0], ast.Constant):
            print("NONCONST word line", node.lineno, ast.unparse(node.args[0]) if node.args else None); continue
        w = node.args[0].value
        keys = {k.arg for k in node.keywords if k.arg}
        star = [ast.unparse(k.value) for k in node.keywords if k.arg is None]
        if w not in allwords:
            print("UNREGISTERED word", w, node.lineno); continue
        for sec, reg in allwords[w]:
            extra = keys - reg
            if extra or star:
                print(f"{node.lineno} {w} [{sec}] extra={sorted(extra)} star={star}")
        if not keys and not star and any(reg for _, reg in allwords[w]):
            print(f"{node.lineno} {w} NO KEYS but registered keyed")
