```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The merge-base delta is scope-clean and its focused checks pass, but two authority conflicts and a false-green scope check make the mission not landable.",
  "workspace": {
    "base_requested": "ed3dd99b",
    "base_mode": "exact",
    "head_start": "ed3dd99b1a24cc321077ee8043d707bcc8261ba2",
    "head_end": "ed3dd99b1a24cc321077ee8043d707bcc8261ba2",
    "upstream_end": "ec8f780337326f82feb1848a972c4746612da6cc",
    "branch": "feat/2026-09-04-fan-skill-distill"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/skill-distill/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "docs/orchestration.md:427; docs/process_traces/2026-09-04-fanout/skill-distill/02-lessons.md:128",
        "text": "The branch installs an executed-probe requirement for every behavioral contract clause and says D-171 resolves it. D-171's dated addendum says the opposite: the probe half is PROPOSAL PENDING ED, applies only under the magistrate's authority to briefs it commissions, and may not be cited as generally ratified. The distillation therefore promotes an explicitly unratified proposal into repository-wide doctrine.",
        "counterfactual": "Input: a behavioral contract edit outside a magistrate-commissioned brief with a valid first-use table but no executed first-use probe. D-171 does not bind it to the probe proposal, while the new orchestration text rejects it; removing the new probe sentence killed policy mutation B9."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "location": "docs/orchestration.md:362; docs/process_traces/2026-09-04-fanout/skill-distill/02-lessons.md:14",
        "text": "The new direct-seat default conflicts with binding D-129, which assigns launch/poll/harvest and other ceremony to Opus subagents and makes Opus-directed Sol lanes the standing default. The cited later budget note records a dated operating regime, but this branch neither amends D-129 nor scopes the new rule to that regime; 02-lessons.md instead says no decision-log change is needed.",
        "counterfactual": "Input: a bounded Sol lane whose role and prompt are fixed and whose Opus wrapper would only launch, poll, and harvest. D-129 routes that ceremony through the Opus-directed default; the new text mandates a direct seat. Removing the direct-seat selection sentence killed policy mutation B3."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "location": "docs/process_traces/2026-09-04-fanout/skill-distill/01-sol-report.md:45",
        "text": "Claimed verification V3 checks only git status, so it cannot detect committed out-of-scope delta paths. In a clean temporary repository whose sole candidate commit added forbidden RUN_STATE.md, the exact V3 command returned WRITE-SCOPE-OK. The mission delta is independently scope-clean, but its mandatory implementation report contains a spoofable scope attestation.",
        "counterfactual": "Input: clean worktree, base commit, then committed RUN_STATE.md delta. Exact V3 returned exit 0 and WRITE-SCOPE-OK while git diff HEAD^..HEAD named RUN_STATE.md."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "location": "docs/process_traces/2026-09-04-fanout/skill-distill/01-sol-report.md:53",
        "text": "V4 exits 0, but its recorded observed.tail is not the exact tail produced by its command: replay emits repository-relative paths and both addendum matches, while the report records shortened lesson paths only. The expected regex is present, so this is evidence-record drift rather than a failed heading inspection.",
        "counterfactual": "Input: exact V4 replay at ed3dd99b. OBSERVED_TAIL_MATCH=False while V4_EXIT=0."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git branch --show-current && git merge-base origin/main HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## feat/2026-09-04-fan-skill-distill...origin/feat/2026-09-04-fan-skill-distill", "ed3dd99b1a24cc321077ee8043d707bcc8261ba2", "feat/2026-09-04-fan-skill-distill", "b0ed6991c11f3a515ad293760c6dfc031adda8e1"]},
      "expected": {"exit_code": 0, "tail_regex": "b0ed6991c11f3a515ad293760c6dfc031adda8e1"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --name-only \"$(git merge-base origin/main HEAD)\"..HEAD && test -z \"$(git diff --name-only \"$(git merge-base origin/main HEAD)\"..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md)\" && echo STATE-DOCS-NO-DELTA",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["docs/agent_playbook.md", "docs/orchestration.md", "docs/process_traces/2026-09-04-fanout/skill-distill/01-sol-report.md", "docs/process_traces/2026-09-04-fanout/skill-distill/02-lessons.md", "STATE-DOCS-NO-DELTA"]},
      "expected": {"exit_code": 0, "tail_regex": "STATE-DOCS-NO-DELTA"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json,pathlib,re,subprocess; t=pathlib.Path(\"docs/process_traces/2026-09-04-fanout/skill-distill/01-sol-report.md\").read_text(); r=json.loads(re.match(r\"```json\\n(.*?)\\n```\",t,re.S).group(1)); xs=[(v[\"id\"],subprocess.run(v[\"cmd\"],shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode) for v in r[\"verification\"]]; print(\" \".join(f\"{i}={c}\" for i,c in xs)); raise SystemExit(any(c for _,c in xs))'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["V1=0 V2=0 V3=0 V4=0 V5=0"]},
      "expected": {"exit_code": 0, "tail_regex": "V1=0 V2=0 V3=0 V4=0 V5=0"}
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'from pathlib import Path; a=Path(\"docs/agent_playbook.md\").read_text(); o=Path(\"docs/orchestration.md\").read_text(); ps=[(\"B1\",a,\"run only the named checks afterward\"),(\"B2\",a,\"PYTHONDONTWRITEBYTECODE=1\"),(\"B3\",o,\"retain a stream director only when\"),(\"B4\",o,\"comparison base\"),(\"B5\",o,\"blind relaunch is prohibited\"),(\"B6\",o,\"compare bytes with the issued artifact\"),(\"B7\",o,\"mode-changing option followed by `--help`\"),(\"B8\",o,\"distinct scratch directory and sealed output\"),(\"B9\",o,\"behavioral\\nclause also needs an executed probe\")]; rs=[(i,s in t,s not in t.replace(s,\"\",1)) for i,t,s in ps]; print(\" \".join(f\"{i}=BASE_PASS/MUTANT_KILLED\" if b and k else f\"{i}=FAIL\" for i,b,k in rs)); raise SystemExit(not all(b and k for _,b,k in rs))'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["B1=BASE_PASS/MUTANT_KILLED B2=BASE_PASS/MUTANT_KILLED B3=BASE_PASS/MUTANT_KILLED B4=BASE_PASS/MUTANT_KILLED B5=BASE_PASS/MUTANT_KILLED B6=BASE_PASS/MUTANT_KILLED B7=BASE_PASS/MUTANT_KILLED B8=BASE_PASS/MUTANT_KILLED B9=BASE_PASS/MUTANT_KILLED"]},
      "expected": {"exit_code": 0, "tail_regex": "B9=BASE_PASS/MUTANT_KILLED"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The direct-seat default and universal executed-probe rule conflict with the current decision-log authority.",
      "needs": "Either obtain and record superseding rulings, or narrow the new doctrine to the authority and dated operating regime already recorded."
    }
  ]
}
```

## Findings

### F1 — blocker: unratified executed-probe proposal installed as doctrine

`docs/orchestration.md:427-431` makes an executed probe mandatory for every
behavioral clause, and `02-lessons.md:132-143` says D-171 resolves that rule.
D-171's controlling addendum at `docs/decision_log.md:10667-10692` says the
probe half is pending Ed, is not generally binding, and may be applied only by
the magistrate to briefs it commissions. This needs a ruling or narrower text.

### F2 — blocker: direct-seat default conflicts with D-129

`docs/orchestration.md:362-366` says to use a direct seat whenever the lead has
fixed the contract and to retain a director only for real mid-stream judgment.
D-129 at `docs/decision_log.md:8318-8332` assigns even launch/poll/harvest
ceremony to Opus subagents and makes Opus-directed Sol lanes the standing
default. The later budget-regime note can support a dated exception or a
superseding ruling, but not an uncited silent replacement while
`02-lessons.md:170-173` says no decision-log change is needed.

### F3 — blocker: committed-scope verification is spoofable

The exact V3 command was run inside a clean temporary repository after a
candidate commit added `RUN_STATE.md`. It returned:

```text
WRITE-SCOPE-OK
COMMITTED_DELTA=RUN_STATE.md
```

The actual mission delta was checked independently from the required merge
base and contains exactly the four paths declared in `01-sol-report.md`; all
four magistrate-owned state paths have no delta. That correct result does not
repair the false-green attestation already embedded in the landing report.

### F4 — should_fix: V4's recorded tail is not its replayed tail

The exact command exits 0 and finds all headings, but a direct comparison
returned `OBSERVED_TAIL_MATCH=False`. The report's shortened seven-line tail is
not exact command output. Replace it with a deterministic summary command or
record the real output.

## Evidence

All five commands claimed by the landing report were extracted from its JSON
and executed at the required head before this review report was written:
`V1=0 V2=0 V3=0 V4=0 V5=0`. No unit-test module was named or changed; per the
task's preflight rule, repository-wide discovery was not run.

The merge-base delta is:

```text
docs/agent_playbook.md
docs/orchestration.md
docs/process_traces/2026-09-04-fanout/skill-distill/01-sol-report.md
docs/process_traces/2026-09-04-fanout/skill-distill/02-lessons.md
STATE-DOCS-NO-DELTA
```

Disposable policy-contract probes exercised each behavioral addition from a
fresh in-memory baseline. Each named phrase was removed once; all mutants were
killed:

| Probe | Counterfactual input | Result |
|---|---|---|
| B1 | task requires focused-only verification | baseline pass; mutant killed |
| B2 | Python test would create unowned bytecode cache | baseline pass; mutant killed |
| B3 | fixed bounded lane with launch/watch-only wrapper | baseline pass; mutant killed |
| B4 | dirty lead checkout plus capped report envelope | baseline pass; mutant killed |
| B5 | wrapper dies after child may have completed | baseline pass; mutant killed |
| B6 | replay has sequential mutants and generated artifact | baseline pass; mutant killed |
| B7 | packet proposes `--bg --help` and omits contrary evidence | baseline pass; mutant killed |
| B8 | two cold seats share scratch before sealing | baseline pass; mutant killed |
| B9 | behavioral clause has vocabulary table but no executed probe | baseline pass; mutant killed |

No previous refuter verdict is present in this directory or repository history
for this path, so there was no mission-specific prior non-staleness blocker to
retest. The current round independently re-tested the spoofable-check and false-
counterfactual classes: V3 false-greened on a forbidden committed path, while
all nine policy mutations were killed.

## Residual risk

The mutation probes establish that the review checks discriminate the added
policy clauses; they do not resolve the authority conflicts in F1 and F2.
