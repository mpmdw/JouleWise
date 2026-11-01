import ast, sys
tree = ast.parse(open(sys.argv[1]).read())
prepare = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_prepare")
reduce_refs = [n for n in ast.walk(prepare) if isinstance(n, ast.Name) and n.id == "_rederive_summary_for_authenticated_fiducial_bound"]
loads = [n for n in ast.walk(prepare) if isinstance(n, ast.Name) and n.id == "rederive" and isinstance(n.ctx, ast.Load)]
calls = [n for n in ast.walk(prepare) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "rederive"]
ok = len(reduce_refs) == 1 and len(loads) == 1 and len(calls) == 1 and calls[0].func is loads[0]
print(sys.argv[1], "reduce_refs", len(reduce_refs), "rederive_loads", len(loads), "direct_calls", len(calls), "PIN", "PASS" if ok else "FAIL")
