```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REFUTE: refusal is incorrectly folded into dominance branch B, and STOP_FILL placeholders lack required omission renderings.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "head_end": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "upstream_end": null,
    "branch": "feat/2026-09-01-skeleton"
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/paper/draft-v2-skeleton.md",
    "docs/paper/round7/survival-map.md"
  ],
  "verdict": {
    "result": "REFUTE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "path": "docs/paper/draft-v2-skeleton.md",
        "line": 364,
        "summary": "A registered refusal is incorrectly made to select branch B."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "path": "docs/paper/draft-v2-skeleton.md",
        "line": 505,
        "summary": "STOP_FILL rows remain raw placeholders instead of their registered omission sentences."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -c 'import re; s=open(\"docs/paper/round7/survival-map.md\").read(); xs=[tuple(map(int,m.groups())) for m in re.finditer(r\"frozen lines (\\d+)[–-](\\d+)\",s)]; c={n:0 for n in range(1,673)}; [c.__setitem__(n,c[n]+1) for a,b in xs for n in range(a,b+1)]; print(f\"ranges={len(xs)} first={xs[0]} last={xs[-1]} gaps={[n for n,v in c.items() if v==0]} overlaps={[n for n,v in c.items() if v>1]}\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ranges=45 first=(1, 8) last=(670, 672) gaps=[] overlaps=[]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^ranges=45 .* gaps=\\[\\] overlaps=\\[\\]$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'import re; sk=open(\"docs/paper/draft-v2-skeleton.md\").read().replace(\"[PREFILL_LENGTH]\",\"<P>\"); reg=open(\"docs/paper/results-fill-registry.md\").read().replace(\"[PREFILL_LENGTH]\",\"<P>\"); raw=re.findall(r\"\\[FILL:([^]]+)\\]\",sk); slots=set(raw)-{\"<registry-row-id>\"}; ids=set(re.findall(r\"^\\| ([A-Z][A-Z0-9-]+) (?:—|\\|)\",reg,re.M)); ids|=set(re.findall(r\"^\\| `\\[([^]]+)\\]`\",reg,re.M)); print(\"fill_occurrences=%d unique=%d missing=%s\" % (len(raw)-1,len(slots),sorted(slots-ids)))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "fill_occurrences=133 unique=84 missing=[]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^fill_occurrences=133 unique=84 missing=\\[\\]$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c 'import re; sk=open(\"docs/paper/draft-v2-skeleton.md\").read().replace(\"[PREFILL_LENGTH]\",\"<P>\"); reg=open(\"docs/paper/results-fill-registry.md\").read().replace(\"[PREFILL_LENGTH]\",\"<P>\"); raw=[x for x in re.findall(r\"\\[FILL:([^]]+)\\]\",sk) if x!=\"<registry-row-id>\"]; stop=[]; [stop.append(x) for x in raw if any((\"STOP_FILL\" in ln and (\"| \"+x+\" \" in ln or \"[\"+x+\"]\" in ln)) for ln in reg.splitlines())]; print(\"stop_occurrences=%d stop_unique=%d\"%(len(stop),len(set(stop))))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "stop_occurrences=50 stop_unique=33"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^stop_occurrences=50 stop_unique=33$"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The requested D-165 close-out ruling path is absent at HEAD; its exact content was inspected from commit 3935bf15.",
      "needs": "Restore or retain the ruling at its requested path if it is intended to be a current-worktree authority."
    }
  ]
}
```

## Findings

1. **BLOCKER — F1.** [draft-v2-skeleton.md:364](/Users/edr/code/JouleWise-wt-skeleton/docs/paper/draft-v2-skeleton.md:364) states: “*At least one required … ratio … was below 2 **or could not be evaluated** …; we therefore withdraw…*”

   The close-out requires a missing, unauthenticated, or zero-denominator result to select **neither** A nor B and stop filling: `docs/process_traces/2026-09-01-fresh-model-review/06b-RULING-d165-artifact-ownership.md:29–34` (exact blob at commit `3935bf15`). This is stricter than D-165’s ratio withdrawal rule at [decision_log.md:192](/Users/edr/code/JouleWise-wt-skeleton/docs/decision_log.md:192).

   Minimal fix: limit B to authenticated evaluable ratios below 2; add a separate refusal disposition saying it selects neither branch and stops filling.

2. **SHOULD-FIX — F2.** The 50 occurrences of 33 `STOP_FILL` rows remain raw `[FILL:…]` slots—e.g. [draft-v2-skeleton.md:505](/Users/edr/code/JouleWise-wt-skeleton/docs/paper/draft-v2-skeleton.md:505)–[513](/Users/edr/code/JouleWise-wt-skeleton/docs/paper/draft-v2-skeleton.md:513) and [draft-v2-skeleton.md:530](/Users/edr/code/JouleWise-wt-skeleton/docs/paper/draft-v2-skeleton.md:530)—rather than the registered omission renderings.

   The checklist makes these complete omission sentences mandatory at [fill-checklist.md:263](/Users/edr/code/JouleWise-wt-skeleton/docs/paper/round7/fill-checklist.md:263)–[297](/Users/edr/code/JouleWise-wt-skeleton/docs/paper/round7/fill-checklist.md:297), including DG-071/DG-075/DS-34 at [fill-checklist.md:248](/Users/edr/code/JouleWise-wt-skeleton/docs/paper/round7/fill-checklist.md:248)–[250](/Users/edr/code/JouleWise-wt-skeleton/docs/paper/round7/fill-checklist.md:250). The registry marks the corresponding table rows `STOP_FILL`, e.g. [results-fill-registry.md:798](/Users/edr/code/JouleWise-wt-skeleton/docs/paper/results-fill-registry.md:798)–[809](/Users/edr/code/JouleWise-wt-skeleton/docs/paper/results-fill-registry.md:809).

   Minimal fix: attach the exact registered omission sentence to each stopped placement, including the G2-a/prompt-pin holds, rather than treating the generic “do not fill” comments as a substitute.

## Coverage check

PASS for the survival-map partition: 45 ranges cover frozen-draft lines 1–672 exactly once, with no gaps or overlaps. Its retained-label handling does not leak the enumerated `_v4` facts into a KEEP verdict; those areas are explicitly rewritten or replaced, including the title/abstract treatment at [survival-map.md:20](/Users/edr/code/JouleWise-wt-skeleton/docs/paper/round7/survival-map.md:20) and the retired-label census at [survival-map.md:436](/Users/edr/code/JouleWise-wt-skeleton/docs/paper/round7/survival-map.md:436).

All 133 explicit fill occurrences (84 unique identifiers) resolve to registry rows, and their table/ledger roles match the registered placement. The R/R_cm construction, equality/zero-denominator rules, 16-unit exact-corner limit, worked arithmetic, G2-a selection/fallback, 37-of-50 negative, fixed-pair non-scaling framing, and sensitivity non-pre-emption were otherwise consistent. No unregistered live `_v5` outcome was stated.

## Residual risk

The requested close-out ruling is not present in this checkout; the branch-rule finding relies on its exact committed blob (`3935bf15`).