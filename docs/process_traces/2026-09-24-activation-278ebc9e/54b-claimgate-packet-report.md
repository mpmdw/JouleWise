```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "clean",
  "completion": "complete",
  "summary": "Assembled six facts-only claim-gate council files within the authorized directory; left them uncommitted.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "bd984da7c2fc1d7c2f2c3876435f522557ac9cb8",
    "head_end": "bd984da7c2fc1d7c2f2c3876435f522557ac9cb8",
    "upstream_end": null,
    "branch": "docs/2026-09-24-278ebc9e-claimgate"
  },
  "pathspec": [
    "docs/process_traces/2026-09-24-activation-278ebc9e/55-claimgate-council-packet/00-question.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/55-claimgate-council-packet/01-current-gate.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/55-claimgate-council-packet/02-simulation-facts.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/55-claimgate-council-packet/03-constraints.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/55-claimgate-council-packet/04-options.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/55-claimgate-council-packet/05-open-facts.md"
  ],
  "unowned_dirty": [],
  "verdict": {"rows": []},
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; import re; p=Path(\"docs/process_traces/2026-09-24-activation-278ebc9e/55-claimgate-council-packet\"); fs=sorted(p.glob(\"*.md\")); assert len(fs)==6; assert all(len(f.read_text().splitlines())<250 for f in fs); assert len(re.findall(r\"^\\d+\\. \", (p/\"05-open-facts.md\").read_text(), re.M))==10; print(\"packet files=6; line limits=pass; spot checks=10\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["packet files=6; line limits=pass; spot checks=10"]},
      "expected": {"exit_code": 0, "tail_regex": "packet files=6; line limits=pass; spot checks=10"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; import re; p=Path(\"docs/process_traces/2026-09-24-activation-278ebc9e/55-claimgate-council-packet\"); refs=[(Path(n),int(i)) for f in p.glob(\"*.md\") for n,i in re.findall(r\"(?<![\\w/])((?:docs|joulewise|scripts)/[^\\s`;|()]+?\\.(?:md|py|csv|json)):(\\d+)\",f.read_text())]; assert refs and all(f.is_file() and i<=len(f.read_text(errors=\"replace\").splitlines()) for f,i in refs); print(f\"citations={len(refs)}; targets=pass\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["citations=114; targets=pass"]},
      "expected": {"exit_code": 0, "tail_regex": "citations=114; targets=pass"}
    }
  ],
  "flags": []
}
```

## Files

[00-question.md](/Users/edr/code/wt-278ebc9e-claimgate/docs/process_traces/2026-09-24-activation-278ebc9e/55-claimgate-council-packet/00-question.md)

- States the D-184 council question.
- Distinguishes effect admission from night equivalence.
- Identifies the one-block floor and block-mean contrast.
- Notes the proposed AP-5M v5 dependency.
- Marks the packet as facts only.

[01-current-gate.md](/Users/edr/code/wt-278ebc9e-claimgate/docs/process_traces/2026-09-24-activation-278ebc9e/55-claimgate-council-packet/01-current-gate.md)

- Traces `claims.py` outcome precedence step by step.
- Records the point-estimate floor check.
- Records direction, TOST, and claim-readiness checks.
- Gives constants and decision provenance.
- Identifies paper routes and the separate D-165 falsifier.

[02-simulation-facts.md](/Users/edr/code/wt-278ebc9e-claimgate/docs/process_traces/2026-09-24-activation-278ebc9e/55-claimgate-council-packet/02-simulation-facts.md)

- Defines the four generating models and cell grids.
- Records 100% misses at 2σ and 84% at 5σ.
- Records interval coverage and diagnostic TOST rates.
- Records the 58% no-change night false-alarm rate.
- Records the proposed rule’s weak ×4-variance detection.

[03-constraints.md](/Users/edr/code/wt-278ebc9e-claimgate/docs/process_traces/2026-09-24-activation-278ebc9e/55-claimgate-council-packet/03-constraints.md)

- Records the attribution limit and later estimand qualification.
- States D-083’s separate-gate rule.
- States D-165’s diagnostic scope.
- Records Ed’s O-21 floor decision.
- Separates existing synthetic evidence from unperformed claims.

[04-options.md](/Users/edr/code/wt-278ebc9e-claimgate/docs/process_traces/2026-09-24-activation-278ebc9e/55-claimgate-council-packet/04-options.md)

- Lists a confidence-bound minimum-effect test.
- Lists TOST with a physical margin.
- Lists dependence-aware bootstrap intervals.
- Lists shared-shock modeling.
- Lists a separate physical floor condition.

[05-open-facts.md](/Users/edr/code/wt-278ebc9e-claimgate/docs/process_traces/2026-09-24-activation-278ebc9e/55-claimgate-council-packet/05-open-facts.md)

- Contains ten cited spot checks.
- Checks the block-mean versus future-block scale.
- Checks interval coverage and TOST admission.
- Checks both night-equivalence rules.
- Checks the open AP-5M floor-unit mapping.

All six files are under 250 lines. Citation targets and line numbers passed inspection. No production tests were run for this documentation-only packet; the files remain uncommitted.