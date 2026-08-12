```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "ACCEPT-FOR-MERGE: F1/F2 are closed and hosted run 31541829071 is green on exact PR #129 head 35f1fe5.",
  "workspace": {
    "base_requested": "fc01220",
    "base_mode": "exact",
    "head_start": "35f1fe52601aa3ae39dc797c8b2e09ec5e8d46fd",
    "head_end": "35f1fe52601aa3ae39dc797c8b2e09ec5e8d46fd",
    "upstream_end": "35f1fe52601aa3ae39dc797c8b2e09ec5e8d46fd",
    "branch": "impl/ci-proof-restructure"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "ACCEPT-FOR-MERGE",
    "findings": [],
    "same_signature": "No surviving F1 or F2 signature: the literal core pin kills all requested registry mutations and the false byte-preservation claim is retracted with no assertion remaining in tracked HEAD text."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git show --stat --oneline 35f1fe5 && git diff --check fc01220..35f1fe5 && git diff --exit-code fc01220..35f1fe5 -- .github/workflows/d117-production-proof.yml",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "tests/test_mint_floor_artifact_generalized.py | 7 +++++++",
          "1 file changed, 7 insertions(+)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1 file changed, 7 insertions"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "for py in python3 python3.11; do \"$py\" -c 'import io,unittest; from tests import test_mint_floor_artifact_generalized as m; core,attack=m.D117_PRODUCTION_PROOF_CORE_LEGS,m.D117_PRODUCTION_PROOF_ATTACK_LEGS; exec(\"for label,mutant in ((\\\"delete\\\",core[1:]),(\\\"phantom\\\",core+(\\\"core-phantom\\\",)),(\\\"reorder\\\",core[::-1])):\\n m.D117_PRODUCTION_PROOF_CORE_LEGS=mutant; m.D117_PRODUCTION_PROOF_LEGS=mutant+attack; m.D117_PRODUCTION_PROOF_PARTITIONS={x:(x,) for x in m.D117_PRODUCTION_PROOF_LEGS}\\n r=unittest.TextTestRunner(stream=io.StringIO()).run(unittest.TestSuite([m.V2PinsetAndMintTests(\\\"test_d117_production_proof_registry_partition_is_exhaustive_and_disjoint\\\")]))\\n assert len(r.failures)==1 and not r.errors and not r.wasSuccessful()\\n print(label+\\\": KILLED\\\")\")'; done",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "delete: KILLED",
          "phantom: KILLED",
          "reorder: KILLED",
          "delete: KILLED",
          "phantom: KILLED",
          "reorder: KILLED"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "reorder: KILLED"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "for py in python3 python3.11; do ruby -ryaml -rjson -e 'puts JSON.generate(YAML.safe_load(File.read(ARGV[0]), aliases: true).fetch(\"jobs\"))' .github/workflows/d117-production-proof.yml | \"$py\" -c 'import json,sys; from tests import test_mint_floor_artifact_generalized as m; j=json.load(sys.stdin); p=j[\"d117-production-proof-plan\"]; w=j[\"d117-production-proof\"]; s=next(x for x in p[\"steps\"] if x.get(\"id\")==\"matrix\"); e=next(x for x in w[\"steps\"] if x[\"name\"].startswith(\"8-9\"))[\"env\"]; legs=tuple(x[\"partition\"] for x in m.d117_production_proof_matrix()[\"include\"]); flat=tuple(y for x in m.D117_PRODUCTION_PROOF_PARTITIONS.values() for y in x); assert set(j)=={\"d117-production-proof-plan\",\"d117-production-proof\"} and \"d117_production_proof_matrix\" in s[\"run\"] and e[\"JOULEWISE_D117_PROOF_PARTITION\"]==\"${{ matrix.partition }}\" and legs==flat==m.D117_PRODUCTION_PROOF_LEGS==tuple(m.D117_PRODUCTION_PROOF_PARTITIONS) and len(set(legs))==len(legs)==22; print(\"workflow/registry binding: PASS; expanded jobs=23; legs=22\")'; done",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "workflow/registry binding: PASS; expanded jobs=23; legs=22",
          "workflow/registry binding: PASS; expanded jobs=23; legs=22"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "expanded jobs=23; legs=22"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest -v tests.test_mint_floor_artifact_generalized",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 50 tests in 3.492s",
          "OK (skipped=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=2\\)"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3.11 -m unittest -v tests.test_mint_floor_artifact_generalized",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 50 tests in 3.927s",
          "OK (skipped=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=2\\)"
      }
    },
    {
      "id": "V6",
      "kind": "other",
      "cmd": "GitHub connector GET /repos/mpmdw/JouleWise/actions/runs/31541829071; fetch run jobs; compare job names with d117_production_proof_matrix()",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "head_branch=impl/ci-proof-restructure; head_sha=35f1fe52601aa3ae39dc797c8b2e09ec5e8d46fd",
          "status=completed; conclusion=success; pr=129; jobs=23/23 success",
          "exact_registry_job_set=true; missing=[]; extra=[]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "jobs=23/23 success"
      }
    },
    {
      "id": "V7",
      "kind": "other",
      "cmd": "gh run view 31541829071 --json headSha,conclusion,jobs",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "error connecting to api.github.com",
          "check your internet connection or https://githubstatus.com"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "35f1fe52601aa3ae39dc797c8b2e09ec5e8d46fd"
      }
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git grep -n -i -E '(byte[- ]preserv.*(monolith|entry point)|(monolith|entry point).*byte[- ]preserv|monolithic entry point.*(unchanged|preserv))' HEAD -- ':!docs/site/**'; git status --porcelain=v1; git rev-parse HEAD; git rev-parse origin/impl/ci-proof-restructure",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "claim scan: no matching tracked HEAD text",
          "worktree porcelain: empty",
          "HEAD and upstream: 35f1fe52601aa3ae39dc797c8b2e09ec5e8d46fd"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "35f1fe52601aa3ae39dc797c8b2e09ec5e8d46fd"
      }
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sandboxed shell could not connect through gh; the authenticated GitHub connector independently fetched the authoritative run and jobs APIs and removed the linkage gap.",
      "needs": ""
    }
  ]
}
```

## Findings

None. Verdict: **ACCEPT-FOR-MERGE**.

Head-linkage evidence: `{"run_id":31541829071,"head_branch":"impl/ci-proof-restructure","head_sha":"35f1fe52601aa3ae39dc797c8b2e09ec5e8d46fd","status":"completed","conclusion":"success","pr_number":129,"pr_head_sha":"35f1fe52601aa3ae39dc797c8b2e09ec5e8d46fd","job_count":23,"completed_success_jobs":23,"non_green_jobs":[]}`

## Residual risk

None material. The two local module skips are expected without a hydrated full-fixture store or selected partition; the exact hosted head executed all 22 strict partitions successfully. The worktree remains clean.