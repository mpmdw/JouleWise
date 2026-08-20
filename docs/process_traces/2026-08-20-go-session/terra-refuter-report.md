```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"REFUTED: the seeded fixture accepts a custody evidence receipt whose pack digest was changed to 64 zeroes.",
  "workspace":{"base_requested":"afb7d57","base_mode":"exact","head_start":"60ddb03","head_end":"60ddb03","upstream_end":null,"branch":"HEAD (detached)"},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"refuted":true,"findings":[{"id":"F1","severity":"blocker","title":"Check mode accepts semantically mismatched mint-custody receipt bytes","evidence":"For each of all three v3 families, emitted generator output plus the four committed custody directories passed --check. Replacing arm_readiness.evidence/evidence-multicell-mint.json's pack_sha256 with 64 zeroes still returned exit 0. The check only derives an inventory from custody JSON; it never validates or byte-compares custody receipts."}]},
  "verification":[
    {"id":"V1","kind":"inspection","cmd":"git diff --find-renames --find-copies afb7d57..60ddb03 -- tests/test_d117_v3_family.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["1 file changed, 74 insertions(+), 16 deletions(-)"]},"expected":{"exit_code":0,"tail_regex":"tests/test_d117_v3_family.py"}},
    {"id":"V2","kind":"smoke","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport json, shutil, subprocess, sys, tempfile\nfrom pathlib import Path\nfrom tests.test_d117_v3_family import FAMILIES, ROOT, generator_command, seed_mint_custody\nfor family in FAMILIES:\n with tempfile.TemporaryDirectory(prefix='d117-refute-') as temp:\n  out=Path(temp); command=generator_command(family,out)\n  assert subprocess.run(command,cwd=ROOT).returncode == 0\n  seed_mint_custody(family,out)\n  receipt=out/'configs/campaigns'/family['v3']/'arm_readiness.evidence'/'evidence-multicell-mint.json'\n  value=json.loads(receipt.read_text()); value['pack_sha256']='0'*64\n  receipt.write_text(json.dumps(value,sort_keys=True,indent=2)+'\\n')\n  assert subprocess.run([*command,'--check'],cwd=ROOT).returncode == 0\nPY","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["All three altered-receipt checks exited 0."]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_v3_family -v","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 5 tests in 12.063s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V4","kind":"smoke","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 [isolated attack harness: emit each v3 family, seed the four directories, corrupt order_manifest.json, delete an evidence sidecar, then run --check]","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Generator-byte corruption: all three checks failed.","Custody-file deletion: all three checks failed.","Altered receipt pack_sha256: all three checks passed."]},"expected":{"exit_code":0,"tail_regex":"checks passed"}}
  ],
  "flags":[]
}
```

## Findings

### F1

`--check` still has teeth for generator-owned byte drift and missing custody files, and the new `missing=order_manifest.json` assertion is discriminating: unrelated calibration-plan byte drift reports generated-file drift instead.

However, a stale/mismatched mint-custody receipt passes. I changed each family’s `arm_readiness.evidence/evidence-multicell-mint.json` `pack_sha256` to all zeroes; all three seeded `--check` runs exited 0. This is a merge-gating fail-open for receipt integrity, so the fix does not survive the requested stale-receipt attack.

## Residual risk

The four listed namespaces are complete for the current three committed v3 packs: each has exactly 37 post-generation residue files, rooted only in those four directories, and seeding them makes each check pass. The pre-overlay non-emission assertions also passed for all three families.