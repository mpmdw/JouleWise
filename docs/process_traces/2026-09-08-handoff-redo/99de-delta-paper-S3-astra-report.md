```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Copy, join, equality and gate checks pass; 20/20 supplied and 2/2 additional kills die. One new structured-refusal defect.",
  "workspace": {
    "base_requested": "ac092ccd",
    "base_mode": "exact",
    "head_start": "ed44276a3a566444a9d83798ae1f6ffeadfd634f",
    "head_end": "ed44276a3a566444a9d83798ae1f6ffeadfd634f",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "feat/2026-09-08-paper-S3"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "joulewise/analysis_engine/claim_side_bound.py",
        "line": 69,
        "summary": "Extreme JSON exponents leak decimal.InvalidOperation through both public APIs.",
        "recommendation": "Handle Decimal conversion failures as structured shape refusals and add regression coverage."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_claim_side_bound",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import runpy, subprocess, sys\nfrom pathlib import Path\nfrom unittest.mock import patch\nns = runpy.run_path('\\''tests/fixtures/paper_custody/run_kills.py'\\'')\np = ns['\\''ROOT'\\''] / ns['\\''BOUND'\\'']\noriginal = p.read_bytes()\nmemory = {p: original}\nreal_run = subprocess.run\ndef write_text(path, value, *a, **k):\n    assert path in (p, Path('\\''/tmp/paper-s3-kills.json'\\''))\n    memory[path] = value.encode()\n    return len(value)\ndef write_bytes(path, value):\n    assert path == p\n    memory[path] = value\n    return len(value)\ndef run(args, **kw):\n    test = args[-1]\n    code = \"import unittest; from joulewise.analysis_engine import claim_side_bound as b; exec(compile(\" + repr(memory[p].decode()) + \", b.__file__, '\\''exec'\\''), b.__dict__); unittest.main(module=None, argv=['\\''unittest'\\'', \" + repr(test) + \"])\"\n    return real_run([sys.executable, '\\''-B'\\'', '\\''-c'\\'', code], **kw)\nwith patch.object(Path, '\\''write_text'\\'', write_text), patch.object(Path, '\\''write_bytes'\\'', write_bytes), patch.object(subprocess, '\\''run'\\'', run):\n    result = ns['\\''run_s3_kills'\\'']()\nassert p.read_bytes() == original\nprint('\\''READ-ONLY: runner writes virtualized; disk bytes unchanged'\\'')\nraise SystemExit(result)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["S3 KILL SUMMARY: 20/20 killed; scoped bytes restored.", "READ-ONLY: runner writes virtualized; disk bytes unchanged"]
      },
      "expected": {"exit_code": 0, "tail_regex": "20/20 killed"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'from tests.test_claim_side_bound import source_fixture, encoded\nfrom joulewise.analysis_engine import claim_side_bound as b\nv,m,f=source_fixture()\nraw=encoded(v).replace(b'\\''\"total\":4.0'\\'',b'\\''\"total\":0e9999999999999999999'\\'')\nkw=dict(finalized_manifest=m,floor_artifact=f)\nleaks=[]\nfor name,call in [('\\''producer'\\'',lambda:b.produce_claim_side_bound(raw,**kw)),('\\''validator'\\'',lambda:b.validate_claim_side_bound(b'\\''{}'\\'',claim_verdicts_raw=raw,**kw))]:\n    try: call()\n    except b.ClaimSideBoundRefusal: pass\n    except Exception as e: leaks.append(name+'\\'':'\\''+type(e).__name__)\nprint('\\'', '\\''.join(leaks))\nassert not leaks, '\\''structured refusal required'\\''\n'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["AssertionError: structured refusal required", "producer:InvalidOperation, validator:InvalidOperation"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Findings

**F1 — should_fix:** At `claim_side_bound.py:69`, `Decimal()` can raise `decimal.InvalidOperation`, which neither public API catches. Executed substitutions `0e9999999999999999999` and `1e-9999999999999999999` both reproduce this. These are valid JSON numerals; the APIs crash instead of returning the documented structured refusal. No copying or licensing bypass was demonstrated.

Executed audit against the synthesis and evidence 10/11:

1. **Copy-only passes.** Traced `_parse → _project → _encode`; independently compared numeral tokens. Total `4.0`, components `1.0/3.0`, CI `[4.147,16.853]`, and decision interval `[0.14700000000000024,20.853]` match exactly. Schema/digest are generated metadata, floor identity comes from the floor, and cells are concatenated; numerical quantities are copied.
2. **Join passes.** Two registered contrasts sharing `[a,b,a]` refuse injectivity. A second ordered join `[b,a,a]` is distinct and accepted; changing sidecar order refuses. A `refused` resolution refuses. The fixture uses v3-shaped contrast registrations without the invented manifest key.
3. **Exact equality passes.** `1e-13` drift, `4.0 → 4`, and `True` replacing numeral `1` all refuse.
4. **Unit boundary passes.** A ratio sidecar relabelled `J` refuses; the `_j` substitute also refuses.
5. **Verdict-only evaluation passes, with a distinction:** edited sidecar intervals cause authentication refusal before evaluation. Isolating the copy guard confirms unchanged verdicts produce identical evaluator inputs, outcome and grants. Editing verdict endpoints and regenerating the sidecar changes `direction_supported → not_resolvable` and removes L2.
6. **Kills pass:** supplied **20/20**; additional **2/2**. My mutations removed duplicate-key rejection and the one-cell requirement for `exact` resolutions. Each positive control passed; each mutant caused an assertion failure.
7. **Contract reconstruction passes for valid inputs.** Independent projection reproduced four numeral-spelling variants byte-for-byte. No undefined mathematical symbols or formula differences found; precedence, averaging, summation and single widening match code.

## Residual risk

Gate probes mocked manifest/verdict-owner/floor-acceptance boundaries; they establish dataflow, not complete custody or hardware validation. The kill runner’s writes were virtualized in memory. All 22 focused tests passed; the full repository suite was not run. Renderer placement remains deferred under D-178. No files changed; head and worktree remained unchanged.