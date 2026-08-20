```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"L5 is STILL-OPEN: no armable current family exists, and F2/F3, coverage, and ED-QUAL-L5-1 remain unclosed.",
  "workspace":{"base_requested":"5bd7acf","base_mode":"exact","head_start":"5bd7acf38fbdd71e77c5da30094e1e6183777697","head_end":"5bd7acf38fbdd71e77c5da30094e1e6183777697","upstream_end":"5bd7acf38fbdd71e77c5da30094e1e6183777697","branch":"HEAD (detached)"},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{
    "seat":"L5-PACK-READINESS-CUSTODY",
    "result":"STILL-OPEN",
    "strongest_reason":"The only minted successor, _v3, is ruled to LAPSE; _v4 is compulsory but unminted, with no fresh dry-run or custody chain.",
    "coverage":{"enumerated_obligations":22,"examined":22,"fully_discharged":2,"unexecuted":["PR #149 hosted Actions-log retrieval","_v3 plan_tree tamper plus regenerated-sidecar falsifier","live successor dry-run","ED-QUAL-L5-1 namespace authoring and validator execution"]},
    "ed_row":{"id":"ED-QUAL-L5-1","status":"STILL-OPEN"},
    "findings":[
      {"id":"L5-F1","severity":"should_fix","disposition":"STILL-OPEN","text":"The bytecode-pollution defect is cured, but the required historical CI truth and runbook cleanup limbs remain unproven."},
      {"id":"L5-F2","severity":"blocker","disposition":"STILL-OPEN","text":"freeze-0003 and U11 receipts bind no plan_tree; preserve-mode --check copies the checked-out bytes into its generated comparison."},
      {"id":"L5-F3","severity":"blocker","disposition":"STILL-OPEN","text":"Only dry-run-0001 exists, bound to _v1/49dcc49; there is no current-family dry-run, arm, or consumption custody."},
      {"id":"L5-F4","severity":"nit","disposition":"STILL-OPEN","text":"_v3 emits truthful frozen wording only with explicit preserve mode; all frozen _v1 packs still report unfrozen draft."},
      {"id":"L5-F5","severity":"nit","disposition":"READY","text":"The M-2 amendment is now the stated governing correction for the old wording divergence."},
      {"id":"L5-COVERAGE","severity":"blocker","disposition":"UNVERIFIED","text":"No independent L5 Phase-3 re-audit or adversarial coverage attack exists."},
      {"id":"ED-QUAL-L5-1","severity":"blocker","disposition":"STILL-OPEN","text":"Raw clock outputs exist, but no arm_readiness.t0.inputs namespace or full validator execution exists."}
    ]
  },
  "verification":[
    {"id":"V1","kind":"inspection","cmd":"git log --oneline -3","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["5bd7acf Merge pull request #160 from mpmdw/integration/phase2-transaction"]},"expected":{"exit_code":0,"tail_regex":"5bd7acf Merge pull request #160"}},
    {"id":"V2","kind":"test","cmd":"cd /private/tmp/jw-l5-audit.oO1gYM/current && env -u PYTHONPYCACHEPREFIX python3 -m unittest tests.test_d117_floor_qwen25_1p5b_plan","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 21 tests in 5.940s","OK","CURRENT_LOCAL_PYCACHE_COUNT=       0"]},"expected":{"exit_code":0,"tail_regex":"Ran 21 tests.*OK"}},
    {"id":"V3","kind":"test","cmd":"cd /private/tmp/jw-l5-audit.oO1gYM/baseline && env -u PYTHONPYCACHEPREFIX python3 -m unittest tests.test_d117_floor_qwen25_1p5b_plan","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["'__pycache__/generate_configs.cpython-313.pyc'","FAILED (failures=1)"]},"expected":{"exit_code":1,"tail_regex":"__pycache__/generate_configs\\.cpython-313\\.pyc"}},
    {"id":"V4","kind":"smoke","cmd":"cd /private/tmp/jw-l5-audit.oO1gYM/current && python3 configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py --check --preserve-current-frozen-bytes","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["verified d117_floor_qwen25_1p5b_v3 frozen by d134 receipt: 100 science configs"]},"expected":{"exit_code":0,"tail_regex":"frozen by d134 receipt"}},
    {"id":"V5","kind":"inspection","cmd":"find /Users/edr/JouleWise-window-custody -name 'dry-run-*.json' -print","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["/Users/edr/JouleWise-window-custody/d117_floor_qwen25_1p5b_v1/arm_readiness.dry_run.receipts/dry-run-0001.json"]},"expected":{"exit_code":0,"tail_regex":"d117_floor_qwen25_1p5b_v1/.*/dry-run-0001\\.json"}},
    {"id":"V6","kind":"inspection","cmd":"rg -o 'plan_tree' configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json | wc -l","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["0"]},"expected":{"exit_code":0,"tail_regex":"^0$"}},
    {"id":"V7","kind":"other","cmd":"gh run list --commit ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b --limit 20","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["error connecting to api.github.com","check your internet connection or https://githubstatus.com"]},"expected":{"exit_code":0,"tail_regex":"STATUS"}}
  ],
  "flags":[
    {"id":"F1","kind":"verification_gap","level":"blocking","text":"The required PR #149 hosted CI-log determination remains unavailable; offline sharding proves the historically failing modules were scheduled.","needs":"Retrieve and custody the relevant Actions shard logs, then record the explanation."},
    {"id":"F2","kind":"baseline_drift","level":"blocking","text":"D-148.5 FINAL rules the _v3 fuse to lapse and compels a _v4 re-freeze with the registry install; no _v4 packs exist at this head.","needs":"Complete the ruled _v4 transaction and re-audit its new evidence/custody chain."}
  ]
}
```

## Findings

**Verdict: STILL-OPEN.** The merge did cure P-13: `git log --oneline -3` puts the executed D-146/D-147 transaction on `main` at `5bd7acf`. That removes the packet’s branch/head ambiguity, but does not create readiness.

My independently enumerated L5 universe was 22 obligations: F1’s three limbs; F2’s binding, execution, and tamper legs; F3’s checkout, registration, and dry-run legs; F4/F5; receipt/digest, fuse, registry, and custody state; Phase-3 re-audit and adversarial coverage; and ED-QUAL-L5-1’s raw-capture and validator legs. I examined 22/22; only two are fully discharged (the F1 code cure and F5’s decision-log wording correction).

- **F1 — STILL-OPEN, should-fix.** The actual bytecode cure works: current 1p5b and 7b plan suites pass (21 and 20 tests), and, with `PYTHONPYCACHEPREFIX` deliberately unset, no pack-local `__pycache__` is created. The historical failure also reproduced at `ac3fe1d` only with local bytecode enabled—this reconciles the apparent conflict with the default environment, which redirects bytecode. However, the required Actions-log explanation remains unavailable and no runbook cleanup note exists. See `ROW-L5.md:174`, `ROW-L5.md:192`, `ROW-L5.md:200`.

- **F2 — STILL-OPEN, blocker.** All three `_v3` freeze and projection receipts have zero `plan_tree` references. More importantly, current preserve-mode generation literally copies all checked-out output bytes into the temporary “generated” tree, so `--check` compares a modified tree to itself; the underlying echo hole remains. `generate_configs.py:1942-1950`, `ROW-L5.md:204-228`. I confirmed explicit preserve-mode `--check` succeeds, but the mutation falsifier itself remains unexecuted.

- **F3 — STILL-OPEN, blocker.** External custody contains only `_v1` `dry-run-0001`; the measurement checkout is at `94dc3b3`, 32 commits behind `5bd7acf`. The arm code properly treats a non-current receipt as `readiness_dry_run_stale` (`joulewise/arm_readiness.py:5881-5930`), and the runbook requires an exact reviewed-head/digest receipt (`window_runbook.md:840-858`). No current-family dry-run, arm, or consumption receipt exists. `ROW-L5.md:235-264`.

- **F4 — STILL-OPEN, nit.** `_v3` with explicit preserve mode now emits truthful “frozen by d134 receipt” wording; bare `--check` refuses, as the stale constant requires. But all three frozen `_v1` packs still exit 0 while saying “unfrozen draft.” This is non-gating, but not fully repaired. `generate_configs.py:185-192`, `:268-278`.

- **F5 — READY.** The M-2 Gate Amendment is now the stated one-home correction: it preserves frozen bytes, strikes the arm-packet citation duty, and scopes M-2 to the three 2026-08-13 hashes. `docs/decision_log.md:9406-9420`.

- **Coverage / Phase 3 — UNVERIFIED, blocker.** No independent focused L5 re-audit or adversarial coverage attack exists; none of `WO-L5-1..3` is tracked in the queue/kernel. `ROW-L5.md:345-350`, `:523-576`. The original 16/18 denominator cannot be accepted.

- **ED-QUAL-L5-1 — STILL-OPEN, blocker.** I confirmed `clock-prior-state.txt` matches the intended `Network Time: On|Off` regex and the raw sudo vectors contain the real `Error:-99` prefix. But no `arm_readiness.t0.inputs` namespace exists, and `_derive_clock_attestation` also requires canonical argv, exit codes, ordering, and capture metadata—not bare output text. `arm_readiness_evidence_t0.py:845-888`; `30-ED-QUALIFICATION-rows.md:258-289`.

The decisive post-packet fact is the D-148.5 FINAL disposition: `_v3` evidence is ruled to **LAPSE**, with `_v4` re-freeze and registry install compelled. No `_v4` packs or v2 registry are present. Thus `_v3` cannot be credited as an armable successor even though its committed receipt digests recompute. `MAGISTRATE-RULING.md:23-41`, `:149-156`.

Sibling adjudication: the packet index explicitly says the sibling numbered set excludes L5, so `rows/ROW-L5.md` is the sole valid L5 assembly; `14-ROW-L5-pack-readiness-custody.md` is seam-reader evidence, not independent L5-grade coverage. Its substantive divergences reconcile as follows: its F1 baseline failure is environment-sensitive and reproduced; its successor “frozen” output is current and correct with preserve mode; its former branch-only claim is superseded by `5bd7acf`. Both records still leave F2, F3, coverage, and the ED row open. `00-INDEX.md:18-25`.

**Single strongest reason:** the council cannot pass L5 while no armable family exists—`_v3` is lapsed by ruling, while `_v4` has not been minted, dry-run, or custodied.

## Residual risk

No additional residual risk beyond the findings. The hosted CI log and live/sudo validation were not performed; both are already explicit closure obligations above.