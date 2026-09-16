```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Appended 16 post-Paper-C research questions in the Astra exploration section, lines 1131–1592.",
  "workspace": {
    "base_requested": "5321659142ec872ff7810040d18e07eaab4a6caa",
    "base_mode": "exact",
    "head_start": "5321659142ec872ff7810040d18e07eaab4a6caa",
    "head_end": "5321659142ec872ff7810040d18e07eaab4a6caa",
    "upstream_end": "5321659142ec872ff7810040d18e07eaab4a6caa",
    "branch": "docs/2026-09-16-rq-bank-exploration"
  },
  "pathspec": ["docs/research_question_bank.md"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -B -c 'from pathlib import Path; import re,subprocess; p=\"docs/research_question_bank.md\"; b=subprocess.check_output([\"git\",\"show\",\"5321659142ec872ff7810040d18e07eaab4a6caa:\"+p]); c=Path(p).read_bytes(); s=c.decode(); h=\"## New questions 2026-09-16 (Astra exploration)\"; a=s.index(h); print(\"append_only=\"+str(c.startswith(b))); print(\"questions=\"+str(len(re.findall(r\"^- \\*\\*RQ-D-A\\d{2}\\b\",s[a:],re.M)))); print(\"section_lines=\"+str(s[:a].count(chr(10))+1)+\"-\"+str(len(s.splitlines())))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["append_only=True", "questions=16", "section_lines=1131-1592"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "append_only=True\\nquestions=16\\nsection_lines=1131-1592"
      }
    }
  ],
  "flags": []
}
```

## Change

Added [the Astra exploration section](/Users/edr/code/JouleWise-wt-rqbank/docs/research_question_bank.md:1131), including Paper C premises, concrete models, mechanisms, controls, floor arithmetic, window budgets, confounds, and five ranked weekly options.

Question IDs: RQ-D-A01, RQ-D-A02, RQ-D-A03, RQ-D-A04, RQ-D-A05, RQ-D-A06, RQ-D-A07, RQ-D-A08, RQ-D-A09, RQ-D-A10, RQ-D-A11, RQ-D-A12, RQ-D-A13, RQ-D-A14, RQ-D-A15, RQ-D-A16.

Next: magistrate review and synthesis with Fable’s exploration.

## Verification notes

No tests, hardware measurements, or commits performed. Original bank bytes remain unchanged; baseline digest matches.

## Residual risk

Window budgets are planning estimates. Runtime support, external-difficulty scoring policy, and second-device gates remain explicit prerequisites.