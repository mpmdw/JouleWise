```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"Production reuse improves fidelity; uncertainty, calibration attachment and power sizing still block confirmation.",
  "workspace":{
    "base_requested":"57a04e4e",
    "base_mode":"exact",
    "head_start":"57a04e4eb6ea45a5395913556e12599945af34af",
    "head_end":"57a04e4eb6ea45a5395913556e12599945af34af",
    "upstream_end":"57a04e4eb6ea45a5395913556e12599945af34af",
    "branch":null
  },
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{
    "decision":"RUN AFTER LISTED FIXES",
    "findings":[
      {"id":"N2","severity":"blocker","title":"Uncertainty excluded from decisions"},
      {"id":"N5","severity":"blocker","title":"Command omits required calibration attachment"},
      {"id":"N1","severity":"blocker","title":"Stage-zero sizing remains unsupported"},
      {"id":"N4","severity":"should_fix","title":"Workload and settling checks remain explicit obligations"}
    ]
  },
  "verification":[{
    "id":"V1","kind":"inspection",
    "cmd":"git status --short --branch; git rev-parse HEAD; git rev-parse origin/main",
    "cwd":".",
    "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","57a04e4eb6ea45a5395913556e12599945af34af","57a04e4eb6ea45a5395913556e12599945af34af"]},
    "expected":{"exit_code":0,"tail_regex":"57a04e4eb6ea45a5395913556e12599945af34af"}
  }],
  "flags":[]
}
```

## Findings

**N2 — Partial cure.** Production removes bespoke anchoring/integration and the internal phase boundary. Endpoints are correct: whole-request net energy/output count; throughput is `(N−1)/(last−first timestamp)`, not mlx_lm’s reported rate. The lead’s fixed 3% margin resolves the margin dispute.

Uncertainty remains blocking. `uncertainty_evidence.py:1563` computes maximum absolute pre/post-idle sample deviation from the pre-idle mean, optionally enlarged by a calibration guard; `reduce.py:473` multiplies by request duration. Thus 32.6 J is a conservative deterministic bound, **not measured drift or a standard error**. It is 16.9% of 193.4 J. Eligibility checks its presence, not adequacy for 3%.

Exact addition:

> “Widen energy decision intervals using production anchor and drift bounds, transformed through token normalization, cell averaging and paired log-ratios. Do not shrink deterministic bounds by √n or assume cancellation. Account for idle-mean uncertainty without double-counting repetition variance. Report both sampling-only and widened intervals; only widened intervals determine verdicts.”

**N5 — New blocker.** Removing tags bypasses custody authentication (`bundle.py:93`, `arm_readiness.py:11437`), without changing numerical measurement algorithms. But B1’s command omits calibration attachment: `controller.py:375` returns none; `reduce.py:2407` adds `instrument_calibration_missing`. Cadence passing is insufficient.

> “Supply a valid matching `--instrument-calibration-dir` and `--instrument-power-policy`; require the complete `idle_subtracted_request` eligibility result. Abort on structural gate failure rather than endlessly rerunning blocks.”

**N1 — Partial cure.** v2.1 fixes multiplicity/stopping rules, conditional on paired-t assumptions. Three agent-active I–SH pairs cannot establish an upper bound on quiet D–I variability. Two runs per cell are acceptable averaging, not doubled replication.

> “Publish power for both contrasts and endpoints across a prespecified SD grid, including pilot-estimation uncertainty and deterministic bounds. Agent-active variability is not presumed conservative. Freeze stage sizes in multiples of six before confirmation; n counts blocks. Include equivalence power and material-difference MDE.”

**N4 — Mostly cured; N3 cured** by v2.1’s contemporary-SH limitation. Production improves workload fidelity, but inherited checks need executable rules:

> “Require 512 observed tokens and matching output-token hashes; reject mismatches. Freeze bounded settling after the CPU probe before the next cell; record unavailable effective-policy observations as unknown.”

## Residual risk

Read-only inspection; no hardware execution or independent smoke-bundle validation. Fixed-workload findings do not establish a universal multiplicative bias for energy per correct answer.