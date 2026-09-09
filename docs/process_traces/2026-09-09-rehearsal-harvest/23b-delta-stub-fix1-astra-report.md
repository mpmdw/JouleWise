```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "S1, N1, S3 and S2 verified; all 139 pins checked; same signature: none.",
  "workspace": {
    "base_requested": "bb7090e2",
    "base_mode": "descendant",
    "head_start": "5db38b5816bce05b67cabfe3eb621bf2b22aa3e6",
    "head_end": "5db38b5816bce05b67cabfe3eb621bf2b22aa3e6",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [],
    "S1": "pass",
    "N1": "pass",
    "S3": "pass",
    "S2": "pass",
    "same_signature": "none"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate.NightGateTests.test_a_green_diagnostic_plan_yields_a_valid_go_receipt tests.test_night_gate.NightGateTests.test_rehearsal_stub_does_not_read_missing_chain_or_sidecar tests.test_night_gate.NightGateTests.test_rehearsal_stub_does_not_read_present_mismatched_chain_or_sidecar",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 3 tests in 0.001s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 3 tests in [0-9.]+s\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import io,subprocess,sys,types,unittest\nfrom unittest.mock import patch\nfrom tests import test_night_gate as t\nname=\"test_rehearsal_stub_does_not_read_present_mismatched_chain_or_sidecar\"\nhead=open(t.night_gate.__file__).read()\nneedle='\\''if plan.receipt_class == \"REHEARSAL_STUB\":\\n        rows[\"C5\"].measured.update('\\''\nassert head.count(needle)==1\nold=subprocess.check_output([\"git\",\"show\",\"bb7090e2:joulewise/night_gate.py\"],text=True)\nfor label,src,want in [(\"baseline\",old,0),(\"forced_read\",head.replace(needle,needle.replace(\" == \",\" != \")),1)]:\n m=types.ModuleType(\"joulewise.audit_\"+label);m.__package__=\"joulewise\";m.__file__=t.night_gate.__file__;sys.modules[m.__name__]=m\n exec(compile(src,m.__file__,\"exec\"),m.__dict__)\n with patch.object(t,\"night_gate\",m):\n  r=unittest.TextTestRunner(stream=io.StringIO()).run(t.NightGateTests(name))\n  assert len(r.failures)==want and not r.errors\n  receipt=t.NightGateTests().evaluate(t.make_plan(\"REHEARSAL_STUB\"),t.FakeProbeSource(chain_digest=\"0\"*64))\n  reason=receipt.refusal.reason if receipt.refusal else None\n  assert reason==(\"night_chain_digest_mismatch\" if want else None)\n  print(f\"{label}: tests={r.testsRun} failures={len(r.failures)} verdict={receipt.verdict} reason={reason}\")\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "baseline: tests=1 failures=0 verdict=REHEARSAL_ONLY reason=None",
          "forced_read: tests=1 failures=1 verdict=REFUSED reason=night_chain_digest_mismatch"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "baseline: tests=1 failures=0 verdict=REHEARSAL_ONLY reason=None\\nforced_read: tests=1 failures=1 verdict=REFUSED reason=night_chain_digest_mismatch"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import ast,re,subprocess,collections\nfrom pathlib import Path\nfiles={\"joulewise/night_gate.py\",\"scripts/run_night.py\",\"tests/test_night_gate.py\",\"tests/test_run_night.py\"}\ndef show(ref,p):return subprocess.check_output([\"git\",\"show\",ref+\":\"+p],text=True,stderr=subprocess.DEVNULL)\np=\"docs/contracts/pack_night_go_receipt.md\";old=show(\"bb7090e2\",p);new=Path(p).read_text()\nrx=re.compile(r\"`([A-Za-z0-9_./-]+\\.(?:py|sh|json|md)):(\\d+)(?:[–-](\\d+))?`(?:[ \\t]+\\(`([A-Za-z_][A-Za-z0-9_.]*)`\\))?\")\na=list(rx.finditer(old));b=list(rx.finditer(new));assert len(a)==len(b)\ncounts=collections.Counter();bare=changed=0\nfor x,y in zip(a,b):\n f,line,end,sym=y.groups()\n if f not in files:assert x.group()==y.group();continue\n changed+=x.group()!=y.group()\n if sym:\n  nodes=ast.walk(ast.parse(Path(f).read_text()))\n  assert any(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and n.name==sym.split(\".\")[-1] and n.lineno==int(line) for n in nodes)\n  counts[f]+=1\n else:\n  _,lo,hi,_=x.groups()\n  assert show(\"83ab38ed\",f).splitlines()[int(lo)-1:int(hi or lo)]==Path(f).read_text().splitlines()[int(line)-1:int(end or line)]\n  bare+=1\ndef norm(s):return rx.sub(lambda m:m.group().replace(\":\"+m.group(2)+((\"–\" if \"–\" in m.group() else \"-\")+m.group(3) if m.group(3) else \"\"),\":PIN\",1) if m.group(1) in files else m.group(),s)\nassert norm(old)==norm(new)\nprint(f\"pins: total={sum(counts.values())+bare} symbol={sum(counts.values())} bare={bare} changed={changed}\")\nprint(dict(sorted(counts.items())))\nprint(\"All symbols match definitions; all 38 bare pins match 83ab38ed content\")\nprint(\"Other-file pin diff: EMPTY; non-target document bytes: IDENTICAL\")\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "pins: total=139 symbol=101 bare=38 changed=63",
          "{'joulewise/night_gate.py': 16, 'scripts/run_night.py': 50, 'tests/test_night_gate.py': 2, 'tests/test_run_night.py': 33}",
          "All symbols match definitions; all 38 bare pins match 83ab38ed content",
          "Other-file pin diff: EMPTY; non-target document bytes: IDENTICAL"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Other-file pin diff: EMPTY; non-target document bytes: IDENTICAL"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "git diff --check bb7090e2..5db38b5816bce05b67cabfe3eb621bf2b22aa3e6",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "using /tmp instead"
      }
    }
  ],
  "flags": []
}
```

## Findings

None.

- **S1 — PASS.** Stub detail equals the dictated sentence byte-for-byte. Non-stub detail equals `bb7090e2` byte-for-byte. Both are pinned by literal `assertEqual` assertions. V1: `Ran 3 tests in 0.001s / OK`, rc=0.
- **N1 — PASS.** Stub C5 measured paths equal the plan’s paths. Runtime comparison against the alternate baseline module confirmed identical evidence lists, with no chain citations. Null digests and the stub marker remain intact.
- **S3 — PASS.** The actual new test passes against the imported `bb7090e2` gate. Inverting only the head’s stub-chain branch predicate kills it:
  ```text
  baseline: tests=1 failures=0 verdict=REHEARSAL_ONLY reason=None
  forced_read: tests=1 failures=1 verdict=REFUSED reason=night_chain_digest_mismatch
  ```
  Mutation harness rc=0; the mutant’s test failure is expected.
- **S2 — PASS.** Checked **139 occurrences: 101 symbol pins and all 38 bare pins**, exceeding the requested sample. **63 changed, 76 unchanged; zero unresolved.** Symbol definition counts: gate 16, driver 50, gate tests 2, driver tests 33. A supplementary scan verified seven symbol annotations outside the same-line parenthesized form.

Representative bare-pin content checks against `83ab38ed`:

| Contract line | Target at head | Matching content |
|---|---|---|
| 152 | `night_gate.py:112–127` | Plan key set |
| 236 | `night_gate.py:1117–1127` | Conditional transaction-unbuilt refusal |
| 644 | `night_gate.py:134–135` | Receipt schema/class keys |
| 767 | `test_run_night.py:1910` | Driver self-authored ARM test definition |
| 854 | `test_run_night.py:2014` | Actual-cause preservation test definition |
| 869 | `night_gate.py:211` | `from_mapping` definition |
| 952 | `test_night_gate.py:414` | Green diagnostic test definition |
| 954 | `test_run_night.py:2306` | Strict custody-root test definition |
| 970 | `night_gate.py:862` | Measurement launcher authentication |
| 974 | `night_gate.py:675` | `_pack_digest` definition |
| 1025 | `night_gate.py:1117–1127` | Conditional transaction-unbuilt refusal |
| 1222 | `night_gate.py:143` | Refusal key set |

V3 tail, rc=0:

```text
All symbols match definitions; all 38 bare pins match 83ab38ed content
Other-file pin diff: EMPTY; non-target document bytes: IDENTICAL
```

Mixed-file table rows appear in the raw diff because their permitted pins moved; their other-file citations remain identical. Removing only permitted pin-number changes leaves identical document bytes.

**same signature: none**

## Residual risk

Verification was limited to the requested delta, three focused tests, and in-memory counterfactuals; the broader suite and live hardware gates were not rerun. No files changed; detached HEAD remained at the requested head. Lead final verification is next.