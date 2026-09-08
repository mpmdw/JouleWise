```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One lineage defect remains; all 90 tests passed without skips, including XD/F4/AQ byte-identical golden replay.",
  "workspace": {
    "base_requested": "c3488fb8455341ffa6fc8d7e12885049bb3dccf8",
    "base_mode": "exact",
    "head_start": "360604220339b25e24aa89bfd14a9d421d77af44",
    "head_end": "360604220339b25e24aa89bfd14a9d421d77af44",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 1, "nit": 0},
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "file": "docs/paper/results-fill-registry.md",
        "line": 778,
        "related_lines": [781],
        "title": "Both supersession annotations omit the immediately preceding reviewed producer bytes",
        "detail": "HEAD~1 pins XS=d6c683fde03c572f0f63b45f6de38f78a03a19275d4c6206837f5f9a5d12623c and AS=3f4f4f122d4992146428696315acbb62341da109f6315285c1a17ef744a33c4b. HEAD instead names 12d0293b... and e3e4355c... as superseded. Those hashes correctly identify the cited older commits, but skip c3488fb8 and therefore do not satisfy C1's immediately preceding digest requirement. Current producer pins are correct.",
        "cmd": "git show HEAD~1:docs/paper/results-fill-registry.md | sed -n '778,781p'; sed -n '778,781p' docs/paper/results-fill-registry.md",
        "recommendation": "Record the HEAD~1 digests with c3488fb8 attribution as the immediate predecessors, retaining the verified older lineage."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS='' R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_excursion_decomposition tests.test_paper_replay_fence tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 90 tests in 642.506s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 90 tests in .*s\\s+OK"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "shasum -a 256 scripts/paper_excursion_decomposition.py scripts/paper_anchor_correction_quantified.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "fc8f17284607621adef3dbf8d14d8c780999fcf74256f46a5934d7b4685b430f  scripts/paper_excursion_decomposition.py",
          "3844a8f1eefb8b898a30b96f524e0af0da3af98fc2e6d0ecb78ea1d1f8d303f1  scripts/paper_anchor_correction_quantified.py"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "3844a8f1eefb8b898a30b96f524e0af0da3af98fc2e6d0ecb78ea1d1f8d303f1"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git show 173fe07e:scripts/paper_excursion_decomposition.py | shasum -a 256; git show b36d1e85:scripts/paper_anchor_correction_quantified.py | shasum -a 256",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "12d0293b2615eaeb872aa5885cad1ac57b853dc975fb5f376a5ce36ef6000688  -",
          "e3e4355c8f388d5e60a4291f3aee4fbd4b4d45217f4156373d6e8dd398b9e693  -"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "e3e4355c8f388d5e60a4291f3aee4fbd4b4d45217f4156373d6e8dd398b9e693"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS='' python3 -B - <<'PY'\nimport ast, hashlib, pathlib, subprocess, tempfile, os\nnames=['paper_excursion_decomposition.py','paper_anchor_correction_quantified.py','check_paper_replay_fence.py']\nblocks=[]\nfor name in names:\n    p=pathlib.Path('scripts')/name\n    raw=p.read_bytes(); lines=raw.splitlines(keepends=True); tree=ast.parse(raw)\n    first=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='BACKUP_PROBE_TIMEOUT_S' for t in n.targets))\n    last=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='probe_backup_root')\n    block=b''.join(lines[first.lineno-3:last.end_lineno]); blocks.append(block)\n    print(name,hashlib.sha256(block).hexdigest())\nassert len(set(blocks))==1\nwith tempfile.TemporaryDirectory(prefix='icloud-delta-mutation-',dir=os.environ.get('TMPDIR')) as d:\n    subprocess.run(['git','clone','--quiet','--shared','--no-checkout','.',d],check=True)\n    subprocess.run(['git','-C',d,'checkout','HEAD','--','scripts','tests'],check=True,stdout=subprocess.DEVNULL)\n    p=pathlib.Path(d)/'scripts/paper_excursion_decomposition.py'\n    p.write_bytes(p.read_bytes().replace(b'BACKUP_PROBE_TIMEOUT_S = 2.0',b'BACKUP_PROBE_TIMEOUT_S = 2.1',1))\n    r=subprocess.run(['python3','-B','-m','unittest','tests.test_paper_excursion_decomposition.BackupHelperIdentityTests'],cwd=d,text=True,capture_output=True)\n    print(r.stderr); assert r.returncode==1 and 'AssertionError: 2 != 1' in r.stderr\nprint('PASS independent helper identity; one-copy mutation killed')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS independent helper identity; one-copy mutation killed"]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS independent helper identity; one-copy mutation killed"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS='' python3 -B - <<'PY'\nimport ast, contextlib, io, pathlib\nfrom unittest import mock\nfor name in ('paper_excursion_decomposition.py','paper_anchor_correction_quantified.py','check_paper_replay_fence.py'):\n    p=pathlib.Path('scripts')/name; raw=p.read_text(); tree=ast.parse(raw)\n    start=raw.index('# Kept verbatim in all three')\n    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='probe_backup_root')\n    block=''.join(raw.splitlines(keepends=True)[raw[:start].count('\\n'):node.end_lineno])\n    for mode in ('is_dir_exception','partial_candidates','published_then_exception'):\n        code=block\n        if mode=='published_then_exception':\n            code=code.replace('result.append(tuple(candidates))','result.append(tuple(candidates))\\n            raise ValueError(\"after publication\")')\n        ns={'__name__':'audit_'+p.stem}\n        exec('from pathlib import Path\\nimport os, logging, threading\\n'+code,ns)\n        def broken_glob(*args,**kwargs):\n            yield pathlib.Path('/synthetic/partial')\n            raise ValueError('after candidate')\n        stderr=io.StringIO()\n        with contextlib.redirect_stderr(stderr), mock.patch.object(pathlib.Path,'is_dir',side_effect=ValueError('directory failure') if mode=='is_dir_exception' else None,return_value=True), mock.patch.object(pathlib.Path,'glob',side_effect=broken_glob if mode=='partial_candidates' else lambda *a: iter([pathlib.Path('/synthetic/complete')])):\n            result=ns['probe_backup_root'](pathlib.Path('/synthetic/root'),'id')\n        assert result==(),(name,mode,result)\n        assert 'backup_root_unavailable reason=worker_error' in stderr.getvalue(),stderr.getvalue()\n        print(name,mode,'zero candidates;',stderr.getvalue().strip())\nprint('PASS all 9 worker exception/partial-publication checks')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS all 9 worker exception/partial-publication checks"]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS all 9 worker exception/partial-publication checks"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "python3 -B - <<'PY'\nimport pathlib, subprocess\npaths=['docs/guides/tutorial-replicate-the-calibration-bound.md','docs/paper/fill-rehearsal-2026-08-27.md','docs/paper/round7/fill-checklist.md']\nfor path in paths:\n    old=subprocess.check_output(['git','show','HEAD~1:'+path]); new=pathlib.Path(path).read_bytes()\n    assert new.startswith(old),path\n    add=new[len(old):].decode()\n    for term in ['2026-09-08','JOULEWISE_BACKUP_ROOTS','os.pathsep','empty value disables','/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup','cumulative 2 s','both globs','responsive-but-slow','zero candidates','fails closed at the pin check']:\n        assert term in add,(path,term)\n    print('PASS append-only policy:',path)\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS append-only policy: docs/paper/round7/fill-checklist.md"]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS append-only policy: docs/paper/round7/fill-checklist.md"}
    }
  ],
  "flags": []
}
```

## Findings

**R1 — should_fix:** `docs/paper/results-fill-registry.md:778` and `:781` skip the immediately preceding reviewed hashes. Add the `c3488fb8` lineage while preserving the correctly attributed older hashes. Current pins and all execution checks pass.