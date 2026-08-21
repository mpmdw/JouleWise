```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The pure-Git historical recomputation and coordinate split are verified; adopt K5 plus the current-tree pin, with K7 retained only as layered delta-shape hardening.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "bea06481275b3b23e9f9777e0ac9206287155d6b",
    "head_end": "bea06481275b3b23e9f9777e0ac9206287155d6b",
    "upstream_end": "bea06481275b3b23e9f9777e0ac9206287155d6b",
    "branch": "impl/d144-followups-prewindow"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "H1",
        "severity": "should_fix",
        "title": "K7 is not independently content-binding",
        "detail": "The measured envelope is correct, but K7 compares only name-status. A coherent rewrite within already-allowed paths preserves K7; K5 validates historical semantics and K12's pinned current D-134 digest supplies the required current-byte binding."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 /private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/rh-opus-scratch/proto.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "MATCH  d117_floor_qwen25_1p5b_v3 1d3873bb7a b170fe0bb02fa29b want b170fe0bb02fa29b nfiles 117 evfiles 0",
          "MATCH  d117_floor_qwen25_7b_v3 1d3873bb7a bd82f7da900a00fe want bd82f7da900a00fe nfiles 117 evfiles 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MATCH.*v3.*want.*"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import glob,json,os,subprocess,collections; packs=sorted({os.path.dirname(os.path.dirname(p)) for p in glob.glob(\"configs/campaigns/*/arm_readiness.evidence/*.json\")}); totals=collections.Counter(); outside=pre=0\nfor pk in packs:\n r=json.load(open(sorted(glob.glob(pk+\"/arm_readiness.evidence/*.json\"))[0])); h=r.get(\"head_commit\") or r.get(\"derivation_commit\"); diff=subprocess.run([\"git\",\"diff\",\"--name-status\",h,\"HEAD\",\"--\",pk],capture_output=True,text=True,check=True).stdout.splitlines(); totals.update(x.split(\"\\t\",1)[0] for x in diff); outside+=sum(x.startswith(\"A\\t\") and x.split(\"\\t\",1)[1][len(pk)+1:].split(\"/\",1)[0] not in {\"arm_readiness.evidence\",\"arm_readiness.freeze.receipts\",\"arm_readiness.sources\",\"identity_pin_projection.receipts\"} for x in diff); tree=subprocess.run([\"git\",\"ls-tree\",\"-rz\",\"--full-tree\",h,\"--\",pk],capture_output=True,check=True).stdout.split(b\"\\0\"); pre+=sum(1 for x in tree if x and x.split(b\"\\t\",1)[1][len(pk.encode())+1:].startswith((b\"arm_readiness.evidence/\",b\"arm_readiness.freeze.receipts/\",b\"arm_readiness.sources/\",b\"identity_pin_projection.receipts/\")))\nprint(f\"packs={len(packs)} additions={totals[chr(65)]} modifications={totals[chr(77)]} deletions={totals[chr(68)]} preauthoring_custody_files={pre} added_outside_custody={outside}\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "packs=9 additions=333 modifications=27 deletions=0 preauthoring_custody_files=0 added_outside_custody=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "packs=9 additions=333 modifications=27 deletions=0 preauthoring_custody_files=0 added_outside_custody=0"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check && git status --short --branch && git rev-parse HEAD @{upstream}",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## impl/d144-followups-prewindow...origin/impl/d144-followups-prewindow",
          "bea06481275b3b23e9f9777e0ac9206287155d6b",
          "bea06481275b3b23e9f9777e0ac9206287155d6b"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "bea06481275b3b23e9f9777e0ac9206287155d6b"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "K7 should be retained as a governed authoring-shape rule, but closure must describe K5 plus the externally pinned current-tree digest as byte-binding.",
      "needs": "Adopt the consolidated rulings below."
    }
  ]
}
```

## Findings

### H1 — should_fix: K7 is not the sole C1 closure

The measured envelope is correct: each pack has 37 added custody paths, zero deletions, and only the observed post-authoring modified paths; all nine historical trees contain zero custody files.

But K7 is pathname/status binding, not content binding. An attacker can alter contents within an already-allowed modified path, coherently repair same-path freeze/plan/sidecar bytes, and leave the exact `head_commit → HEAD` name-status envelope unchanged. K5 remains true because the historical claim is still honest. K7 passes.

K12’s pinned current D-134 digest rejects that mutation. Therefore: K5 is mandatory for false historical claims; K12 is mandatory for current-byte integrity; K7 is valuable extra hardening that constrains the legitimate authoring shape.

## Residual risk

The static pinset and its literal test hash are governance/review controls, not independent protection against an actor who can rewrite history, pinset, test, and published anchors together.

## Adjudication

1. **DISPUTED** — 9/9 historical matches and the 37-add/0-delete envelope are verified. I do not concede “K7, not K5” as the closure: K7 misses same-path content rewrites. Adopt K5 + K12 as load-bearing; retain K7.

2. **CONCEDED** — the plan binding must be checked at `HEAD`. `plan_tree.json` and its sidecar differ between each receipt’s historical commit and `HEAD` in all 9/9 packs. My design was coordinate-ambiguous; a historical-plan implementation would refuse the corpus.

3. **CONCEDED** — use a disjoint `histsem_*` vocabulary owned by `receipt_histsem.py`. My proposed new `arm_readiness.py` refusal would trigger the 47-code cardinality pin, registry/census test, and committed-source evidence derivation. Leave `READINESS_REASON_CODES` untouched.

4. **CONCEDED** — use the small `scripts/generate_arm_readiness.py` seam for both `freeze` and `arm`; source search found no non-test production caller of either core generator. I withdraw the direct-core-hook demand. Preserve a test that the reviewed CLI refuses before either operation.

5. **AGREED** — create the `_v4` pinset row during `_v4` S5, after final freeze artifacts are known and before the transaction is accepted. Retrofitting it later recreates the ungoverned “expected value after the fact” problem.

6. **DISPUTED** — no executed evidence refutes the pure-Git prototype; I independently confirmed its 9/9 digest result and all-nine HEAD differential equivalence. I withdraw my historical-plan ambiguity, in-core reason-code proposal, and direct-core seam preference; the K7-as-sole-closure wording remains refuted.

## Consolidated rulings

1. Implement pure-Git `ls-tree` + `cat-file` historical hashing with the existing D-134 framing and an all-nine `HEAD` differential test.
2. Keep two coordinates explicit: historical `head_commit` for K5/K6, `HEAD` for receipt/freeze/plan binding and current-tree pinning.
3. Require K5, K12, and K7 together; describe K7 as delta-shape hardening, not sole byte integrity.
4. Use disjoint `histsem_*` errors and gate both CLI `freeze` and `arm`.
5. Mint the `_v4` pinset row within S5, never as retrospective resealing.