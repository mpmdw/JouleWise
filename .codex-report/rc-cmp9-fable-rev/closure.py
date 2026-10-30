"""RC-CMP9-FABLE-REV answer 4: are REGISTERED_SOURCES closed? (a) every file the registry reads is pinned and named;
(b) expected_checks and the helpers it calls read only module constants and the registry (no file, env, L9 or
recompute input); (c) the table is built in one place."""
import dis
import re
import sys
import types

sys.path.insert(0, "/home/user/JouleWise")
from scripts import compare_b5_recompute as cmp  # noqa: E402

read = []
real = cmp.Registry.read


def spy(self, root, name, pins):
    read.append(name)
    return real(self, root, name, pins)


cmp.Registry.read = spy
registry = cmp.Registry()
cmp.Registry.read = real
files = {s for s in cmp.REGISTERED_SOURCES if s.startswith("configs/")}
print("(a) files the registry read:", sorted(read))
print("    REGISTRY_PINS keys     :", sorted(cmp.REGISTRY_PINS))
print("    REGISTERED_SOURCES files:", sorted(files))
print("    read == pinned:", set(read) == set(cmp.REGISTRY_PINS))
print("    pinned ⊆ named:", {"configs/campaigns/" + k for k in cmp.REGISTRY_PINS} <= files)
print("    named − pinned:", sorted(files - {"configs/campaigns/" + k for k in cmp.REGISTRY_PINS}))
print("    pins hold on this checkout (no refusal):", bool(registry.tables["contrast"]))

seen, stack, names = set(), [cmp.expected_checks], {}
while stack:
    fn = stack.pop()
    if fn in seen or not isinstance(fn, types.FunctionType):
        continue
    seen.add(fn)
    globs = sorted(n for n in fn.__code__.co_names if n in fn.__globals__)
    names[fn.__name__] = globs
    for n in globs:
        value = fn.__globals__[n]
        if isinstance(value, types.FunctionType) and value.__module__ == cmp.__name__:
            stack.append(value)
print("(b) functions reached from expected_checks:", sorted(names))
suspicious = {"open", "Path", "json", "os", "sys", "environ", "load_registry", "custody", "read_text", "read_bytes",
              "loads", "labelled", "Documents", "STEP11_SOURCES"}
for fn, globs in sorted(names.items()):
    kinds = {}
    for n in globs:
        v = cmp.__dict__.get(n, None)
        kinds[n] = type(v).__name__
    flagged = [n for n in globs if n in suspicious]
    print(f"    {fn}: globals={globs} flagged={flagged}")
print("    argument of expected_checks:", cmp.expected_checks.__code__.co_varnames[:cmp.expected_checks.__code__.co_argcount])

src = open(cmp.__file__).read()
adds = [m.start() for m in re.finditer(r"\btable\.append\(|\badd\(\"", src)]
lines = {src.count("\n", 0, i) + 1 for i in adds}
start = src.index("def expected_checks(")
end = src.index("\ndef ", start + 10)
inside = {n for n in lines if src.count("\n", 0, start) + 1 <= n <= src.count("\n", 0, end) + 1}
print("(c) table.append / add( sites:", len(lines), "inside expected_checks:", len(inside), "outside:", sorted(lines - inside))
print("    compare_expected builds the table from custody.registry only:",
      "expected_checks(custody.registry)" in src[src.index("def compare_expected"):src.index("def closed_items")])
# (d) the table is the same for two registries loaded independently, and it has no value from any output.
a, b = cmp.expected_checks(registry), cmp.expected_checks(cmp.Registry())
print("(d) two independently loaded registries give equal tables:", a == b, "entries:", len(a))
