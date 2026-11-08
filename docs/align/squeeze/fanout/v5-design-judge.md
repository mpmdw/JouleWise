# v5-design-judge — Sol1 handoff

Brief dated 2026-11-08; design review only. Branch:
`align/2026-11-08-v5design-judge-sol1`.

Built [the independent judgment](../v5-design/sol1-sol1.md): five available
seats scored on all five requested dimensions, an exact hybrid recommendation,
Sol/Opus agreements and disagreements, source commit inventory, replay and
night-cost arithmetic, RTX 3050 use/limits, and lead-ruling table.

Recommendation: fresh behavioral experiment/calibration using groundup-Sol2's
backbone, v4 engineering reuse, actual writable-record/offload attacks, strong
software comparison, development-gated metered replay, and desktop pilots plus
physical replication. Do not make Flash-Next or imputed attack energy primary
dependencies. Full primary metered replay provisionally raises the Sol2 primary
reserve from 438.63 h to 673.00 h; it is not a free extra channel.

## Provenance and open questions

- `GIT_ALLOW_PROTOCOL=file git fetch origin` failed, exit 128, HTTPS transport
  disallowed to enforce the binding no-network rule. No refresh occurred.
  Five cached origin seats were read completely; groundup-sol1 was absent
  locally. Remote existence/freshness remains unknown. The judgment pins every
  reviewed commit and the tripwire-directions source at `028a70529246…`.
- The judgment's final table lists required lead decisions. The first is to
  refresh/read the missing seat, then approve a capability-and-cost charter.
- Assumed the supplied meter, monitor, D-139, calibration, control, estimand,
  three-layer framing and desktop-resource rulings. Did not reinterpret them
  as authorization to run hardware, buy a meter, download weights or call APIs.
- Pilot quantities, replay resolution and model rates are documentary premises.
  All v5 capability, 900 s timing, tail closure, software coverage, replay
  exactness and desktop resolution remain uncertain and unvalidated.
- The R1 integrated lane, sealed data and measurement jobs were untouched.
  No coordination-state files, kernel tasks, code or repository tests changed.

## Verification

Temporary audit module:
`/private/tmp/v5-design-judge-sol1/test_v5_design_judgment.py`.
It uses stdlib arithmetic, pinned Git refs and the requested document only.

Command, one module in one process:

```sh
GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null PYTHONPATH=/private/tmp/v5-design-judge-sol1 python3.13 -B -m unittest test_v5_design_judgment
```

Failing first: 9 checks ran; 8 passed and the delivery check failed because
the judgment did not yet exist. After authoring: **9/9 passed**, 0.050 s.
Checks cover five-seat delivery/pins, v4 roster typo and reuse hours,
groundup-Sol2 budgets, additional measured replay, groundup-Opus qualification
overflow, rank/tolerance/cluster bounds, exact binomial planning power and
replay-unit arithmetic. They validate bookkeeping, not the scientific premise.
`git diff --cached --check` passed; final staged review covered only these two
documents.

No full suite, analysis pipeline, model execution, compileall, MLX or native
hardware test was run: only two Markdown files changed. The lead must validate
native MLX generation/replay on the selected model, side-generation and
subprocess controls, matched DC-in replay nulls and battery closure in a clean
authorized hardware session. The desktop CUDA backend and wall-meter path
need their own qualification. No native test is claimed passed here.

## Files and local commit

- `docs/align/squeeze/v5-design/sol1-sol1.md`
- `docs/align/squeeze/fanout/v5-design-judge.md`

Local commit message: `docs(align): judge v5 designs and recommend native hybrid`.
No push. Final commit ID is supplied in the user-facing handoff.
