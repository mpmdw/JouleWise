```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One blocker: the packer's terminal-block predicate still lets a two-live-owner forgery pass sealing; one should-fix fuzz diagnostic defect. All 71 scored tests pass.",
  "workspace": {
    "base_requested": "0fa4e6e3",
    "base_mode": "exact",
    "head_start": "0fa4e6e3bdb55e1cf4129cd4b027a4c00b54f97e",
    "head_end": "0fa4e6e3bdb55e1cf4129cd4b027a4c00b54f97e",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "A1": "FAIL: text 3's terminal-block predicate is not implemented literally in the packer.",
    "A2": "PASS: all eleven named regressions GREEN at head and RED with only the test file swapped into the baseline archive; some baseline errors are missing-helper errors.",
    "A3": "PASS: positive controls correct, every pairwise ratio <= 0.30 and every control <= 0.28.",
    "A4": "PASS: protected schemas, registration keys, roles and cell structure unchanged.",
    "A5": "FAIL: composed two-live-owner forgery survives sealing; replay subsequently rejects it. No cache bypass or valid-roster population discrepancy found. Internal refusals: zero.",
    "A6": "Historical 2.8-second baseline timing reproduced; head takes approximately 5.1-5.2 seconds for the corresponding call. No finite registration-size maximum exists.",
    "findings": [
      {
        "id": "AUD-1",
        "severity": "blocker",
        "path": "joulewise/scored_packer.py",
        "line": 234,
        "summary": "INV-11 uses an item-specific, block-id-specific terminal test instead of the contract's all-items-terminal block predicate.",
        "witness": "Two distinct live blocks holding L1I0 and L1I1 pass _structure, _seal(finalize=True), and verification-mode _seal; checker reports INV-11. Requeue rejects later with inv_38.",
        "cure": "Compute terminal-block status from all block items' (model,item) membership in terminal_refusals, independent of refusal block_id; add the composed forgery and partial-terminal contrast regressions."
      },
      {
        "id": "AUD-2",
        "severity": "should_fix",
        "path": "tests/test_scored_packer_fuzz.py",
        "line": 186,
        "summary": "Checker crashes become stringified tuples, so the bare-string checker-crash assertion at line 206 cannot detect them.",
        "witness": "Injected TypeError from check_roster for 30 submissions; test_a passed with zero failures and errors.",
        "cure": "Keep a dedicated checker-error field or immediately fail with contextual diagnostics; test the injected checker-crash path."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest -v tests.test_scored_registration tests.test_scored_packer tests.test_scored_roster_checker tests.test_scored_packer_fuzz tests.test_scored_packer_stress",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 71 tests in 1095.844s", "OK", "GENERATOR signatures differ 60/60"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest -v tests.test_scored_packer",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 37 tests in 10.391s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest -v tests.test_scored_packer",
      "cwd": "/tmp/278ebc9e/a291audit/base",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 37 tests in 4.445s", "FAILED (failures=5, errors=6)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=5, errors=6\\)"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/similarity.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["METHOD VALID", "SCREEN PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "SCREEN PASS"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/scope.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["SCOPE PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "SCOPE PASS"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/two_live.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["STRUCTURE ACCEPT", "FINALIZE ACCEPT", "VERIFY-SEAL ACCEPT", "REQUEUE inv_38: event replay"]},
      "expected": {"exit_code": 0, "tail_regex": "VERIFY-SEAL ACCEPT"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/fuzz_details.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["INV52_DETAILS {'malformed roster': 23}", "INTERNAL 0", "LEGAL {'legal_requeue': 95} final 4 non_ok 0"]},
      "expected": {"exit_code": 0, "tail_regex": "INTERNAL 0"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "python3 -B -m unittest -v tests.test_scored_packer_fuzz",
      "cwd": "/tmp/278ebc9e/a291audit/fuzzbase",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 6 tests in 60.666s", "FAILED (failures=3)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=3\\)"}
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/cure_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["CURE TWO_LIVE inv_11: item conservation", "Ran 37 tests in 11.483s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V10",
      "kind": "inspection",
      "cmd": "PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/checker_crash_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["checker crash submissions 30", "test_a failures 0 errors 0 passed True", "dedicated-marker cure: test_a failures 1 errors 0 passed False"]},
      "expected": {"exit_code": 0, "tail_regex": "dedicated-marker cure: test_a failures 1"}
    },
    {
      "id": "V11",
      "kind": "other",
      "cmd": "PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/cost.py baseline",
      "cwd": "/tmp/278ebc9e/a291audit/base",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["baseline n=64 size=2 root_loaded=128 input_events=130 output_events=131 seconds=2.808928,2.787660,2.816711"]},
      "expected": {"exit_code": 0, "tail_regex": "output_events=131"}
    },
    {
      "id": "V12",
      "kind": "other",
      "cmd": "PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/cost.py head",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["head n=64 size=2 root_loaded=128 input_events=130 output_events=131 seconds=5.227412,5.105284,5.210492"]},
      "expected": {"exit_code": 0, "tail_regex": "output_events=131"}
    },
    {
      "id": "V13",
      "kind": "other",
      "cmd": "python3 -B scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 2, "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]},
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    }
  ],
  "flags": [
    {
      "id": "PERF",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Registration size is unbounded by the contract, and current-head replay is slower than the historical baseline.",
      "needs": "Retain B2's requirement to remeasure and record per-call cost before an arm whose pack root exceeds 60 loaded envelopes."
    },
    {
      "id": "ENV",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The session-end fixture census could not invoke ps under the sandbox; no clean census is claimed.",
      "needs": "Lead runs the census in a permitted environment."
    }
  ]
}
```

## Findings

| ID | Severity | Finding and executed witness | Cure |
|---|---|---|---|
| AUD-1 | **BLOCKER** | [scored_packer.py:234](/Users/edr/code/wt-278ebc9e-a291audit/joulewise/scored_packer.py:234) defines terminal status using the current item and matching refusal `block_id`. Contract 02d:62 defines a terminal **block** as one whose **every item is terminal**. A composed forgery with two distinct live owners passes both seal modes. | Derive terminal-block status from all `(model, item)` pairs, independently of refusal `block_id`. Add the composed forgery and the partly-terminal contrast as regressions. A scratch-only correction rejected the forgery with `inv_11` and passed all 37 packer tests. |
| AUD-2 | **should_fix** | [test_scored_packer_fuzz.py:186](/Users/edr/code/wt-278ebc9e-a291audit/tests/test_scored_packer_fuzz.py:186) stores `"('checker-crash', 'TypeError')"`, while line 206 compares against `"checker-crash"`. Thirty injected checker exceptions produced a green `test_a`. | Preserve a dedicated error marker/field or fail immediately with operator/seed context. Preserving the bare marker made the existing assertion fail correctly. |

AUD-1 does **not** bypass replay: the forged roster is rejected by `requeue_overrun` with `inv_38`. It nevertheless violates the required pre-arithmetic INV-11 seal check and reproduces the two-live-owner defect at that boundary.

**A1 — Final texts v4: FAIL on text 3.**

| Text | Implementation location and verdict |
|---|---|
| 1, A291-POP-1 | `joulewise/scored_packer.py:80,106`; `tests/scored_roster_checker.py:273` — PASS for fact populations, spread, null rules, arithmetic and emptiness. |
| 2, boundary/order/detail | `joulewise/scored_packer.py:134,251,476`; detail helpers at `tests/test_scored_packer.py:23`, `tests/test_scored_packer_fuzz.py:29`, `tests/test_scored_roster_checker.py:37` — PASS. |
| 2a, fact builder/lever | `joulewise/scored_packer.py:80,106,130` — PASS: six fact keys, both modes, ordered guards, single-return `_derived`. |
| 3, preconditions | `joulewise/scored_packer.py:169,225,234,236`; checker at `tests/scored_roster_checker.py:578` — **FAIL: AUD-1**, packer terminal-block predicate differs from the binding definition and checker. Other specified rows are present. |
| 4, `_live_index` | `joulewise/scored_packer.py:70` — PASS; duplicate block-ID listings refuse, `_live` is absent. |
| 5, trust-cache deletion | `joulewise/scored_packer.py:22,392` — PASS; unconditional external-entry replay, no trusted-output cache; B2 residual recorded in P’s report. |
| 6, regressions/helper | `tests/test_scored_packer.py:16,414` — PASS for the specified tests and reseal behavior; A2 qualifies the baseline error modes. |
| 7, K deliverables | `tests/scored_roster_checker.py:249,273,832`; `tests/test_scored_roster_checker.py:145,830`; `tests/scored_case_generator.py:99`; `tests/test_scored_packer_fuzz.py:156,204` — specified deliverables PASS; additional diagnostic defect AUD-2. |
| 8, integration/scope/screen | `tests/test_scored_packer_stress.py:110,124`; `tests/test_scored_packer.py:75` — PASS. Protected functions and original E1–E11 assertions remain unchanged; scope and similarity checks pass. |

**A2 — PASS, with explicit baseline failure modes.**

Baseline preparation:

```sh
mkdir -p /tmp/278ebc9e/a291audit/base
git archive 20cd29de | tar -x -C /tmp/278ebc9e/a291audit/base
cp tests/test_scored_packer.py /tmp/278ebc9e/a291audit/base/tests/test_scored_packer.py
```

Only that test file was replaced for this comparison. Command in each checkout:

```sh
python3 -B -m unittest -v tests.test_scored_packer
```

| Regression | `0fa4e6e3` | `20cd29de` |
|---|---|---|
| R1 | GREEN | RED: `stale_derived`, expected `inv_11` |
| R2 | GREEN | RED: raw `ZeroDivisionError` |
| R2b | GREEN | RED: `stale_derived`, expected `inv_12` |
| R3 | GREEN | RED: raw `ZeroDivisionError` |
| R4a | GREEN | RED: missing `_parent_facts` |
| R4b | GREEN | RED: missing `_parent_facts` |
| R4c | GREEN | RED: AST assertion |
| R4d | GREEN | RED: raw `ZeroDivisionError` |
| R4d-facts | GREEN | RED: missing `_parent_facts` |
| R5a | GREEN | RED: no refusal |
| R5b | GREEN | RED: trusted cache present |

Tails:

```text
HEAD:
Ran 37 tests in 10.391s
OK

BASE:
Ran 37 tests in 4.445s
FAILED (failures=5, errors=6)
```

R4a’s red baseline result is **not** evidence of a numerical difference: it fails at the added helper inspection before reaching its literal-value assertion.

The integrated five-module command and tail:

```sh
python3 -B -m unittest -v tests.test_scored_registration tests.test_scored_packer tests.test_scored_roster_checker tests.test_scored_packer_fuzz tests.test_scored_packer_stress
```

```text
Ran 71 tests in 1095.844s
OK
FUZZ cases=4 submissions=1798 census={'inv_02': 808, 'inv_03': 99, 'inv_11': 447, 'inv_12': 41, 'inv_38': 372, 'inv_39': 8, 'inv_52': 23}
GENERATOR seed=291013 cases=60 edges={'E1': 298, 'E10': 170, 'E11': 30, 'E2': 432, 'E3': 1041, 'E4': 212, 'E5': 54, 'E6': 84, 'E7': 95, 'E8': 24, 'E9': 7}
GENERATOR seed=291014 cases=60 edges={'E1': 311, 'E10': 171, 'E11': 36, 'E2': 480, 'E3': 1122, 'E4': 206, 'E5': 61, 'E6': 89, 'E7': 75, 'E8': 24, 'E9': 8}
GENERATOR signatures differ 60/60
STRESS seed=291013 registrations=300 calls=4263 checker_calls=4863 violations=0 edges={'E1': 262, 'E10': 76, 'E11': 37, 'E2': 1027, 'E3': 186, 'E4': 224, 'E5': 38, 'E6': 260, 'E7': 74, 'E8': 223, 'E9': 37}
STRESS seed=291014 registrations=300 calls=4253 checker_calls=4853 violations=0 edges={'E1': 262, 'E10': 76, 'E11': 37, 'E2': 1028, 'E3': 186, 'E4': 224, 'E5': 38, 'E6': 260, 'E7': 74, 'E8': 223, 'E9': 37}
```

**A3 — PASS. Exact script executed:**

```sh
PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/similarity.py
```

```python
import ast, inspect, io, keyword, subprocess, tokenize
from joulewise import scored_packer as sp
from tests import scored_roster_checker as ck
from tests.test_scored_roster_checker import refresh_derived

def normal(src):
    src = ast.unparse(ast.parse(src))
    result, row = [], []
    for t in tokenize.generate_tokens(io.StringIO(src).readline):
        if t.type in (tokenize.NEWLINE, tokenize.NL):
            if row:
                result.append(' '.join(row)); row = []
        elif t.type in (tokenize.INDENT, tokenize.DEDENT, tokenize.COMMENT, tokenize.ENDMARKER):
            continue
        else:
            row.append('N' if t.type == tokenize.NAME and not keyword.iskeyword(t.string)
                       else '#' if t.type == tokenize.NUMBER else t.string)
    return result

def score(src, ref):
    xs, ys = normal(src), set(normal(ref))
    matched = [x for x in xs if x in ys]
    return len(matched), len(xs), matched

def pinned(path):
    return subprocess.check_output(['git', 'show', '20cd29de:' + path], text=True)

def functions(src):
    return {n.name: ast.get_source_segment(src, n) for n in ast.parse(src).body
            if isinstance(n, ast.FunctionDef)}

old = functions(pinned('tests/scored_roster_checker.py'))
pold = functions(pinned('joulewise/scored_packer.py'))
original = old['_derived']
chunks = original.splitlines(keepends=True)
def offset(line, col):
    return sum(map(len, chunks[:line - 1])) + col
replacements = []
for node in ast.walk(ast.parse(original)):
    if isinstance(node, ast.Assign):
        v = node.value
        expr = ast.get_source_segment(original, v)
        toks = [t.string for t in tokenize.generate_tokens(io.StringIO(expr).readline)
                if t.type not in (tokenize.NEWLINE, tokenize.NL, tokenize.INDENT,
                                  tokenize.DEDENT, tokenize.ENDMARKER)]
        replacements.append((offset(v.lineno, v.col_offset), offset(v.end_lineno, v.end_col_offset),
                             '(\n' + '\n'.join(toks) + '\n)'))
variant = original
for start, end, value in sorted(replacements, reverse=True):
    variant = variant[:start] + value + variant[end:]
same = ast.unparse(ast.parse(variant)) == ast.unparse(ast.parse(original))
valid = same
print('P2 canonical_equal', same)
for label, src in [('P1', original), ('P2', variant)]:
    n, d, _ = score(src, pold['_derived'])
    print(f'{label} {n}/{d}={n/d:.6f}')
    valid &= (n, d) == (29, 33)

sources = functions(inspect.getsource(ck))
primary = {'_derived': ck._derived, 'check_executed': ck.check_executed,
           'refresh_derived': refresh_derived}
targets = {'_derived': ['_parent_facts', '_lever', '_derived'],
           'check_executed': ['executed_status', '_parent_facts', '_lever'],
           'refresh_derived': ['_parent_facts']}
def direct(src):
    return {n.func.id for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in sources}
def reach(src):
    seen, todo = set(), list(direct(src))
    while todo:
        name = todo.pop()
        if name not in seen:
            seen.add(name); todo.extend(direct(sources[name]) - seen)
    return seen
changed = {name for name, src in sources.items() if old.get(name) != src}
print('CHANGED', sorted(changed))
reaches = {name: reach(inspect.getsource(fn)) for name, fn in primary.items()}
H = set().union(*reaches.values()) & changed
H = {name for name in H if len(normal(sources[name])) >= 5}
print('H', sorted(H))
for h in sorted((set().union(*reaches.values()) & changed) - H):
    print('SHORT_HELPER', h, len(normal(sources[h])))
passed = True
for name, fn in primary.items():
    print('REACH', name, sorted(reaches[name]))
    src = inspect.getsource(fn)
    for label, body in [(name, src)] + [(h, inspect.getsource(getattr(ck, h))) for h in sorted(H & reaches[name])]:
        count = len(normal(body))
        print('LINES', name, label, count)
        if count < 5:
            print('NOT_SCORED', label); continue
        for target in targets[name] + ['_structure']:
            n, d, matches = score(body, inspect.getsource(getattr(sp, target)))
            bound = .28 if target == '_structure' else .30
            ok = n / d <= bound
            print(f'PAIR {name}:{label} -> {target} {n}/{d}={n/d:.6f} bound={bound:.2f} {"PASS" if ok else "FAIL"}')
            if label in H:
                print('MATCHED', repr(matches))
            if target == '_structure': valid &= ok
            passed &= ok
print('METHOD', 'VALID' if valid else 'INVALID')
print('SCREEN', 'PASS' if valid and passed else 'FAIL')
raise SystemExit(0 if valid and passed else 1)
```

Every number and the complete reachability/matched-line output:

```text
P2 canonical_equal True
P1 29/33=0.878788
P2 29/33=0.878788
CHANGED ['_derived', '_static_checks', '_unreported', '_window_keys_ok', '_window_of', 'check_executed']
H ['_derived', '_static_checks', '_window_of']
SHORT_HELPER _unreported 2
SHORT_HELPER _window_keys_ok 2
REACH _derived ['_items', '_roles', '_window_of']
LINES _derived _derived 27
PAIR _derived:_derived -> _parent_facts 4/27=0.148148 bound=0.30 PASS
MATCHED ['def N ( N , N , N = None ) :', 'for N in N :', 'if ( N , N ) in N :', 'for N in N :']
PAIR _derived:_derived -> _lever 5/27=0.185185 bound=0.30 PASS
MATCHED ['for N in N :', 'for N in N ( N ) :', 'N = { }', 'for N in N :', 'return ( N , N )']
PAIR _derived:_derived -> _derived 1/27=0.037037 bound=0.30 PASS
MATCHED ['def N ( N , N , N = None ) :']
PAIR _derived:_derived -> _structure 4/27=0.148148 bound=0.28 PASS
MATCHED ['for N in N :', 'for N in N ( N ) :', 'N = { }', 'for N in N :']
LINES _derived _window_of 15
PAIR _derived:_window_of -> _parent_facts 0/15=0.000000 bound=0.30 PASS
MATCHED []
PAIR _derived:_window_of -> _lever 2/15=0.133333 bound=0.30 PASS
MATCHED ['N = { }', 'return ( N , N )']
PAIR _derived:_window_of -> _derived 0/15=0.000000 bound=0.30 PASS
MATCHED []
PAIR _derived:_window_of -> _structure 1/15=0.066667 bound=0.28 PASS
MATCHED ['N = { }']
REACH check_executed ['_append_placement', '_apply', '_bad', '_cap', '_check_predictions', '_check_registration_impl', '_decide', '_derived', '_eligible', '_event_checks', '_gap', '_hex', '_int', '_items', '_num', '_parent_id', '_parent_of', '_parents', '_roles', '_root_from_final', '_schema', '_static_checks', '_types', '_unreported', '_window_keys_ok', '_window_of', '_worst', 'canon', 'canon_sha', 'check_registration', 'check_roster', 'digest', 'preimage']
LINES check_executed check_executed 12
PAIR check_executed:check_executed -> executed_status 2/12=0.166667 bound=0.30 PASS
PAIR check_executed:check_executed -> _parent_facts 1/12=0.083333 bound=0.30 PASS
PAIR check_executed:check_executed -> _lever 1/12=0.083333 bound=0.30 PASS
PAIR check_executed:check_executed -> _structure 1/12=0.083333 bound=0.28 PASS
LINES check_executed _derived 27
PAIR check_executed:_derived -> executed_status 1/27=0.037037 bound=0.30 PASS
MATCHED ['N , N = N ( N , N , N )']
PAIR check_executed:_derived -> _parent_facts 4/27=0.148148 bound=0.30 PASS
MATCHED ['def N ( N , N , N = None ) :', 'for N in N :', 'if ( N , N ) in N :', 'for N in N :']
PAIR check_executed:_derived -> _lever 5/27=0.185185 bound=0.30 PASS
MATCHED ['for N in N :', 'for N in N ( N ) :', 'N = { }', 'for N in N :', 'return ( N , N )']
PAIR check_executed:_derived -> _structure 4/27=0.148148 bound=0.28 PASS
MATCHED ['for N in N :', 'for N in N ( N ) :', 'N = { }', 'for N in N :']
LINES check_executed _static_checks 143
PAIR check_executed:_static_checks -> executed_status 2/143=0.013986 bound=0.30 PASS
MATCHED ['def N ( N , N , N , N ) :', 'N ( N , N , N )']
PAIR check_executed:_static_checks -> _parent_facts 12/143=0.083916 bound=0.30 PASS
MATCHED ['N = N ( N )', 'N = N ( N )', 'for N in N :', "if N [ 'parent_block_id' ] is not None :", 'for N in N :', "N = { ( N [ 'model' ] , N [ 'item_id' ] ) for N in N [ 'terminal_refusals' ] }", 'for N in N :', 'for N in N :', 'for N in N :', 'continue', 'N = N ( N )', 'return N']
PAIR check_executed:_static_checks -> _lever 6/143=0.041958 bound=0.30 PASS
MATCHED ['for N in N :', 'for N in N :', 'for N in N :', 'for N in N :', 'for N in N :', 'N = { }']
PAIR check_executed:_static_checks -> _structure 22/143=0.153846 bound=0.28 PASS
MATCHED ['N = N ( N )', 'N = N ( N )', 'if N is not None :', 'N = { N : { } for N in N }', "for N in N [ 'blocks' ] :", "if N [ 'parent_block_id' ] is None :", "N [ N [ 'model' ] ] . N ( N ( N [ 'items' ] , N [ 'predicted_item_s' ] ) )", 'for N in N :', "for N in N [ 'blocks' ] :", 'for N in N :', 'for N in N :', 'for N in N :', "for N , N in N ( N [ 'envelopes' ] ) :", "if N [ 'kind' ] == 'idle_slot' :", "N = N [ 'blocks' ] + N [ 'voided_block_ids' ]", 'for N in N :', 'N = { }', "for N in N [ 'blocks' ] :", 'else :', 'if N is None :', 'continue', 'N = N ( N )']
LINES check_executed _window_of 15
PAIR check_executed:_window_of -> executed_status 0/15=0.000000 bound=0.30 PASS
MATCHED []
PAIR check_executed:_window_of -> _parent_facts 0/15=0.000000 bound=0.30 PASS
MATCHED []
PAIR check_executed:_window_of -> _lever 2/15=0.133333 bound=0.30 PASS
MATCHED ['N = { }', 'return ( N , N )']
PAIR check_executed:_window_of -> _structure 1/15=0.066667 bound=0.28 PASS
MATCHED ['N = { }']
REACH refresh_derived []
LINES refresh_derived refresh_derived 23
PAIR refresh_derived:refresh_derived -> _parent_facts 1/23=0.043478 bound=0.30 PASS
PAIR refresh_derived:refresh_derived -> _structure 2/23=0.086957 bound=0.28 PASS
METHOD VALID
SCREEN PASS
```

`H` includes `_derived` because `check_executed` reaches it; that additional screening also passes. The checker’s ownership walk is `(model, item)` at line 266, with registration-slice aggregation at line 292; the packer walks parents at line 85.

**A4 — PASS.**

Executed [scope.py](/tmp/278ebc9e/a291audit/scope.py):

```sh
PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/scope.py
```

```text
registration schemas joulewise.scored_registration.v2 joulewise.scored_roster.v3
registration keys 29 ['alpha', 'anchor_j', 'arm', 'arm_to_family', 'block_size', 'budget_j', 'cap_tokens', 'ceiling_s', 'declared_sensitivities', 'delta_upper_j_per_block_slot', 'envelope_s', 'floor_j', 'guard_s', 'interior_s', 'item_ids_by_level', 'mode', 'n_boot', 'offset_s', 'pitch_s', 'plan_id', 'predictions_sha256', 'prefill_s', 'registration_id', 'role_to_model_id', 's_per_token_upper', 'schema', 'scorer_id', 'seed', 'sizing_receipt_sha256']
roster keys 14 ['blocks', 'claim_ready', 'drift_lever_slots', 'envelopes', 'events', 'item_set_sha256', 'n_per_level', 'placements', 'planned_spread_shortfall', 'registered_sha256', 'registration_sha256', 'schema', 'sha256', 'terminal_refusals']
roles {'8B': 'large', '1.7B': 'small'}
cells 10 ['large:1', 'large:2', 'large:3', 'large:4', 'large:5', 'small:1', 'small:2', 'small:3', 'small:4', 'small:5']
levels ['1', '2', '3', '4', '5']
UNCHANGED registration source, nested roster key sets, roster top-level keys, roles/items helpers, checker constants
UNCHANGED run_case/_report/old stress test/r2_four_envelope_roster/public checker signatures/packer test lines 30-40
SCOPE PASS
```

The seven-file diff does not change contract documents or runner sequencing. FT-6 role ordering, FT-7 cell shape, FT-9 sequencing, and FT-10 null semantics remain intact.

**A5 — FAIL: AUD-1 survives; the other two classes were not reproduced.**

The [two-live witness](/tmp/278ebc9e/a291audit/two_live.py) starts with a real one-event history, appends a differently named copy of a parent in another loaded envelope, and adds terminal entries naming the original parent’s items. It refreshes derived values test-side before finalization.

```sh
PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/two_live.py
```

```text
STRUCTURE ACCEPT
FINALIZE ACCEPT
VERIFY-SEAL ACCEPT
LIVE L1I0 [('large:decode:1:0', 0), ('large:decode:1:999', 11)]
LIVE L1I1 [('large:decode:1:0', 0), ('large:decode:1:999', 11)]
CHECKER ['INV-10', 'INV-11', 'INV-37', 'INV-38', 'INV-41', 'INV-50']
REQUEUE inv_38: event replay
```

Additional call-site hunts, from [extra.py](/tmp/278ebc9e/a291audit/extra.py):

```sh
PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/extra.py
```

```text
duplicate FINALIZE inv_11: item conservation
duplicate CHECKER ['INV-11', 'INV-25', 'INV-27', 'INV-36', 'INV-38', 'INV-41', 'INV-49']
refinalized EXECUTED inv_38: event replay
refinalized CHECKER ['INV-30', 'INV-38']
partial EXECUTED/CHECKER/REFRESH 1.5999999999999996 gate=4 position=5 spread=True
omitted sibling EXECUTED/CHECKER 0.0 gate=4 position=4
all-terminal-live STRUCTURE ACCEPT
all-terminal-live FINALIZE ACCEPT
all-terminal-live CHECKER ['INV-11', 'INV-37', 'INV-38']
all-terminal-live REQUEUE inv_38: event replay
part-terminal-live STRUCTURE inv_11: item conservation
part-terminal-live CHECKER ['INV-25', 'INV-37', 'INV-38', 'INV-49']
```

Thus the original duplicate-ID route is closed; `executed_status` does not trust a re-finalized forgery; and executed/checker/fixture derivations agree on the additional partly-terminal and omitted-window populations. Distinct gate and position populations remain intentional under A291-POP-1.

The [scratch cure probe](/tmp/278ebc9e/a291audit/cure_probe.py) replaced only the terminal predicate in memory:

```sh
PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/cure_probe.py
```

```text
CURE TWO_LIVE inv_11: item conservation
.....................................
----------------------------------------------------------------------
Ran 37 tests in 11.483s

OK
```

Fuzz detail census:

```sh
PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/fuzz_details.py
```

```text
FUZZ 1798 {'inv_02': 808, 'inv_03': 99, 'inv_11': 447, 'inv_12': 41, 'inv_38': 372, 'inv_39': 8, 'inv_52': 23}
INV52_DETAILS {'malformed roster': 23}
INTERNAL 0
LEGAL {'legal_requeue': 95} final 4 non_ok 0
OPERATOR_RESEALED_NON_DIGEST {'op1_live_to_voided': 99, 'op2_duplicate_live_placement': 99, 'op4_add_terminal': 99, 'op6_flip_superseded': 99, 'op7_move_placement': 99, 'op8_flip_late': 99, 'op10_increment_attempt': 99, 'op3_drop_terminal': 92, 'op9_alter_event_digest': 91, 'op5_remove_single': 23}
```

For the baseline fuzz check, a separate archive received the head’s checker, generator and fuzz module. Baseline production code remained unchanged:

```sh
# cwd: /tmp/278ebc9e/a291audit/fuzzbase
python3 -B -m unittest -v tests.test_scored_packer_fuzz
```

```text
FAIL: test_a_entry_points_return_or_raise_packing_refusal
FAIL: test_b_checker_violation_implies_refusal
FAIL: test_d_refusal_census
Ran 6 tests in 60.666s
FAILED (failures=3)
FUZZ cases=4 submissions=1798 census={'inv_02': 334, 'inv_03': 198, 'inv_38': 508, 'inv_39': 8, 'inv_52': 46, 'stale_derived': 696}
```

Properties (a)/(b) fail on eight raw `ZeroDivisionError` submissions; (d) lacks `inv_11` and `inv_12`.

AUD-2’s [injection probe](/tmp/278ebc9e/a291audit/checker_crash_probe.py):

```sh
PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/checker_crash_probe.py
```

```text
checker crash submissions 30
stored checker diagnostic ["('checker-crash', 'TypeError')"]
test_a failures 0 errors 0 passed True
dedicated-marker cure: test_a failures 1 errors 0 passed False
```

**A6 — Historical cost reproduced; current head is slower; no largest permitted registration.**

[Cost probe](/tmp/278ebc9e/a291audit/cost.py) builds the specified mode-0 histories using baseline production, then times the final requeue three times. Baseline cache is cleared before every timed call. These final samples ran sequentially after the suite finished:

```sh
# cwd: /tmp/278ebc9e/a291audit/base
PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/cost.py build
PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/cost.py baseline

# cwd: audit checkout
PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/cost.py head
```

```text
BUILT cost-2-11.json events 15 root_loaded 12
BUILT cost-4-64.json events 67 root_loaded 64
BUILT cost-2-64.json events 131 root_loaded 128

baseline n=11 size=2 root_loaded=12 input_events=14 output_events=15 seconds=0.050743,0.048556,0.048588
baseline n=64 size=4 root_loaded=64 input_events=66 output_events=67 seconds=0.778718,0.765375,0.750050
baseline n=64 size=2 root_loaded=128 input_events=130 output_events=131 seconds=2.808928,2.787660,2.816711

head n=11 size=2 root_loaded=12 input_events=14 output_events=15 seconds=0.057951,0.055252,0.055320
head n=64 size=4 root_loaded=64 input_events=66 output_events=67 seconds=1.426757,1.420523,1.429090
head n=64 size=2 root_loaded=128 input_events=130 output_events=131 seconds=5.227412,5.105284,5.210492
```

The historical **2.8 seconds** is reproduced at baseline; **47 ms/729 ms** are approximately reproduced, not established as current upper bounds. The current head takes approximately **5.1–5.2 seconds** on the corresponding 130→131 call.

Replay processes a triangular number of historical transitions over a night; those transitions themselves have growing roster-processing costs. The quadratic replay warning is real, but should not be read as a tight wall-time bound.

Contract §2.1 permits equal-length item lists with `n ≥ 1` and no upper bound. Registration validation likewise has no size ceiling:

```sh
PYTHONPATH=. python3 -B /tmp/278ebc9e/a291audit/registration_bound.py
```

```text
ACCEPT n_per_level 64 items 320 parents 320
ACCEPT n_per_level 128 items 640 parents 640
ACCEPT n_per_level 10000 items 50000 parents 50000
NO FINITE CONTRACT MAXIMUM: n >= 1, equal-length five lists; block_size >= 1; no upper bound
```

Next exact step: correct AUD-1, add its composed witness, repair AUD-2’s diagnostic handling, and return the resulting head for delta verification. Preserve the existing pre-arm remeasurement duty above 60 loaded root envelopes.

## Residual risk

The similarity screen establishes low normalized overlap, not independent authorship. Executed probes and the finite fuzz corpus do not prove absence of all malformed-input variants. The repository-wide canonical suite was not run; all five requested scored modules completed successfully.

These were agent-active software timings, not quiet-machine hardware validation. The required fixture census exited 2 because `ps` was denied:

```text
{"error": "PermissionError: [Errno 1] Operation not permitted: 'ps'"}
```

The checkout remains clean and detached at `0fa4e6e3`. All audit artifacts are under `/tmp/278ebc9e/a291audit/`; no repository files were modified.