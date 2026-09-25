```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "blocked",
  "completion": "partial",
  "summary": "Seven factual council packet files are written and checked; sandbox permissions blocked the requested commit.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "4a78cc021386aaaee405ec258360c0aae9f628c7",
    "head_end": "4a78cc021386aaaee405ec258360c0aae9f628c7",
    "upstream_end": null,
    "branch": "docs/2026-09-24-278ebc9e-packets"
  },
  "pathspec": [
    "docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/00-directive-407.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/01-q1.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/02-q2.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/03-q3.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/04-q4.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/05-q5.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/06-open-facts.md"
  ],
  "unowned_dirty": [],
  "verdict": {"rows": []},
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "ls docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["00-directive-407.md", "01-q1.md", "02-q2.md", "03-q3.md", "04-q4.md", "05-q5.md", "06-open-facts.md"]},
      "expected": {"exit_code": 0, "tail_regex": "06-open-facts.md"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "sed -n '349p' joulewise/analysis_engine/claims.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["if margin is None or margin <= 0.0 or method != \"tost_v1\":"]},
      "expected": {"exit_code": 0, "tail_regex": "tost_v1"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git add docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 128, "tail": ["fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/wt-278ebc9e-packets/index.lock': Operation not permitted"]},
      "expected": {"exit_code": 0, "tail_regex": ""}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "Git metadata for this worktree is outside the writable sandbox; git add could not create index.lock, so no commit was made.",
      "needs": "Lead to stage and commit the seven packet files on this branch; do not push."
    }
  ]
}
```

## Packet files

[Directive](</Users/edr/code/wt-278ebc9e-packets/docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/00-directive-407.md>), [Q1](</Users/edr/code/wt-278ebc9e-packets/docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/01-q1.md>), [Q2](</Users/edr/code/wt-278ebc9e-packets/docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/02-q2.md>), [Q3](</Users/edr/code/wt-278ebc9e-packets/docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/03-q3.md>), [Q4](</Users/edr/code/wt-278ebc9e-packets/docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/04-q4.md>), [Q5](</Users/edr/code/wt-278ebc9e-packets/docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/05-q5.md>), and [open facts and ten pasted line checks](</Users/edr/code/wt-278ebc9e-packets/docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/06-open-facts.md>).

## Facts by question

**Q1**
- The review specifies a 32k-token trace, 1k-token bins, a quadratic fit and an alternative-attention contrast.
- The admitted Qwen3 1.7B and 8B weights are local 4-bit MLX trees with declared 40,960-token contexts.
- No suitable alternative-attention 4-bit tree was established in the local inventory.
- The current quiet protocol has twelve 600-second envelopes within 9,000 seconds; continuous-trace duration remains unmeasured.
- A3 needs a new registration and night design; the frozen _v5 decode workload is fixed at 512 tokens, and Q2 G2-a is the ready quiet task.

**Q2**
- The KM003C archive contains a probe, protocol material and timestamped watt readings.
- No KM003C reader was found in the searched repository code paths.
- The MLX runtime records prefill, first-token/decode and token events.
- The admitted Qwen3 panel covers 4-bit weights; other bit widths need artifacts and pins.
- B1 overlaps E214’s gain-check lane but adds phase and bit-width comparisons; meter accuracy and clock alignment remain open.

**Q3**
- The proposed AP-5M text fixes two models, a single arm cap and a crossover-level headline.
- Ed later conditionally authorized E2, delegated E3/E4, resolved E1 to ids and hashes, and answered O-21 yes.
- The packet identifies the affected O-items, AP-5M T-texts and A291 FT-texts.
- A291’s current registration and roster contract encodes two model roles and five levels; A2 adds caps and A1 adds votes and a model.
- That redesign intersects the active A291 packer and the dependent A292 reducer and A293 estimator.

**Q4**
- Workload token timestamps use `SystemClock.now()`, which reads wall time; `stamp()` also brackets a wall read with monotonic reads.
- The _v5 generator assigns A-B-B-A in every block, and its prospective manifest calls the order deterministic.
- D-165 registers a per-component ratio threshold of 2 and a comparative common-mode withdrawal rule.
- `claims.py` already contains `tost_v1`, interval checks and `effect_not_above_floor`.
- The review’s dominance probability and claimed √n scale error remain simulation questions; changing ABBA order would alter frozen registration and pack identity.

**Q5**
- Orchestration already has cost-based review tiers.
- Its merge rule and twelve-row PR ledger still require multiple reviews, final-head review and terminal lead review.
- Ed made `gate-ledger` a required main-branch check after the workflow comments called it advisory.
- Registrations, reducers, estimators and claim admission are clear claim paths; clock and runner changes can also alter measurement evidence.
- A one-reviewer rule would require a cold-gated process amendment and matching ledger/tooling changes.

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Q1–Q4 | needs_ruling | Council design decision | _v5 registration, quiet-night slots, AP-5M and A291 contracts |
| Q5 | needs_ruling | Process cold gate and council | Orchestration merge rule and PR ledger |

## Critical path

A291’s contract precedes A292’s reducer. AP-5M’s adopted text precedes A293’s estimator. Q2 G2-a occupies the current ready quiet-machine lane; a new A3 or B1 night needs its own registered slot.

## Verification and blocker

All seven files are under 250 lines. The citation scan found **91 resolving repository file-line references**, and the whitespace scan passed. Ten `sed -n` outputs are pasted in [06-open-facts.md](</Users/edr/code/wt-278ebc9e-packets/docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/06-open-facts.md>); tails include `"context_window": 40960,`, `"window_max_s": 9000`, `ABBA_POSITIONS = (("A", "A1"), ("B", "B1"), ("B", "B2"), ("A", "A2"))`, and the `tost_v1` condition.

**Commit pending:** `git add` failed because the sandbox denied creation of the worktree’s `index.lock` under `/Users/edr/code/JouleWise/.git`. The files remain untracked on the requested branch. The next exact step is to stage and commit this packet directory from a session with write access to that Git metadata; no push is needed.