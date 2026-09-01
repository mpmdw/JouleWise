```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Applied all accepted A1–A28 and B1–B4 cures to PROJECT_STATUS.md and passed every required verification.",
  "workspace": {
    "base_requested": "db77383ffe66b7755d314f5a5683ab38ccfcb7df",
    "base_mode": "exact",
    "head_start": "db77383ffe66b7755d314f5a5683ab38ccfcb7df",
    "head_end": "db77383ffe66b7755d314f5a5683ab38ccfcb7df",
    "upstream_end": "db77383ffe66b7755d314f5a5683ab38ccfcb7df",
    "branch": "feat/2026-09-01-status-rewrite"
  },
  "pathspec": [
    "PROJECT_STATUS.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_paper_terms_lint tests.test_gen_state",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "...........................................",
          "----------------------------------------------------------------------",
          "Ran 43 tests in 1.903s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 43 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "missing_count=0\nwhile IFS= read -r path; do\n  if [[ ! -e \"$path\" ]]; then\n    print -r -- \"missing: $path\"\n    missing_count=$((missing_count + 1))\n  fi\ndone < <(rg -o '`[^`]+`' PROJECT_STATUS.md | tr -d '`' | rg '^[A-Za-z0-9_.-]+/' | rg -v '^github[.]com/')\nif (( missing_count == 0 )); then\n  print 'all PROJECT_STATUS repository pointers resolve'\nelse\n  exit 1\nfi",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "all PROJECT_STATUS repository pointers resolve"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "all PROJECT_STATUS repository pointers resolve"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "terms=$(sed -n '/Plain-language terms used throughout:/,/Freshness and authority:/p' PROJECT_STATUS.md | rg -o '\\*[^*]+\\*' | tr -d '*' | awk '!seen[tolower($0)]++')\nbad=0\nwhile IFS= read -r term; do\n  first=$(rg -n -i -m1 -F -- \"$term\" PROJECT_STATUS.md)\n  count=$(rg -i -o -F -- \"$term\" PROJECT_STATUS.md | wc -l | tr -d ' ')\n  first_line=$(printf '%s' \"$first\" | cut -d: -f1)\n  printf '%s | first %s | uses %s\\n' \"$term\" \"$first_line\" \"$count\"\n  if (( count < 2 )); then bad=1; fi\ndone <<< \"$terms\"\nexit \"$bad\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Frozen | first 10 | uses 14",
          "Prospective | first 12 | uses 8",
          "Admitted | first 14 | uses 4",
          "gate | first 16 | uses 15",
          "Governed | first 18 | uses 10",
          "measurement window | first 20 | uses 2",
          "run bundle | first 21 | uses 6",
          "pack | first 23 | uses 15",
          "detection floor | first 25 | uses 2",
          "mint | first 27 | uses 7",
          "arm | first 29 | uses 5",
          "verdict | first 30 | uses 5",
          "refusal | first 31 | uses 9",
          "cell | first 32 | uses 6",
          "component | first 33 | uses 5",
          "state kernel | first 35 | uses 2",
          "manifest | first 36 | uses 4",
          "Strict validation | first 38 | uses 5",
          "Finalization | first 39 | uses 5",
          "results fill | first 41 | uses 4",
          "transaction | first 44 | uses 4",
          "Telemetry | first 45 | uses 12",
          "tokenizer | first 47 | uses 3"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tokenizer \\| first 47 \\| uses [2-9][0-9]*"
      }
    }
  ],
  "flags": []
}
```

## Change

Updated [PROJECT_STATUS.md](/Users/edr/code/JouleWise-wt-status/PROJECT_STATUS.md) with all accepted pedagogy, replication, and factual cures. The frozen paper was untouched; no measurement ran and no commit was created.

## Findings table

| ID | Cure | Line | Verified against |
|---|---|---:|---|
| A1 | Built registered semantics and explained hash visibility | 79–88 | `generate_configs.py:2597-2603`; `test_d117_contrast_v5_pack.py:444,518-544` |
| A2 | Defined the four calibrated boundary corners, exact common-shift scan, interval-corner maximum, and max—not sum—composition | 104–113 | `joulewise/reduce.py:2148-2268`; `joulewise/detection_floor.py:859-970`; `docs/decision_log.md:192` |
| A3 | Defined a rung at first use | 134–146 | `scripts/select_g2a_prefill_length.py:17-23,98-120`; `docs/decision_log.md:193` |
| A4 | Defined a four-run paired block at first use; removed all earlier uses | 94–103 | `joulewise/detection_floor.py:1270-1286` |
| A5 | Defined frozen before pack uses it | 10–24 | `docs/contracts/analysis_plans.md:69-103` |
| A6 | Stated timing-aware ÷ naive order | 115–128 | `feat/d165-dominance-closeout-core:joulewise/dominance_closeout.py:191-212` |
| A7 | Replaced model-family wording with independently run review sessions, consistent with B4 | 159–162 | `00-MAGISTRATE-SYNTHESIS.md:3-8`; Opus review `:80` |
| A8 | Defined shakedown as the real-pack pre-claim proof | 148–157 | `docs/process/state_kernel.json:4653-4719` |
| A9 | Defined desk day as non-measurement analysis work | 148–157 | `docs/process/state_kernel.json:4533-4646` |
| A10 | Replaced ambiguous “ruled follow-ups” | 310, 485–486 | `docs/process/v5-artifact-flow.md:19-25` |
| A11 | Split evidence-to-prose chain into physical program actions | 469–477 | `docs/process/v5-artifact-flow.md:10-17` |
| A12 | Explained Window A as the July calibration campaign | 191–196 | `docs/stream_logs/2026-07-17-topdocs.md:8-14` |
| A13 | Replaced six labels with granularity-based plain prose | 193–196 | `docs/reviews/2026-07-19-measurement-soundness-audit.md:43-56` |
| A14 | Explained the machine-environment guard | 203–207 | `docs/decision_log.md:4055-4097`; `measurement_methodology.md:38-70` |
| A15 | Replaced “members” with runs | 441–450 | `docs/decision_log.md:193`; selector `:18,105` |
| A16 | Explained Qwen3 reasoning-off and deterministic token choice | 462–465 | `docs/decision_log.md:193` |
| A17 | Renamed split-inference ladder to three-stage | 538 | `docs/phase_3/phase_3_plan.md:43-50` |
| A18 | Replaced roots with separate directories and consequence | 466–467 | `docs/process/state_kernel.json:4832` |
| A19 | Defined whole-window verdict and replaced claim engine | 325–328 | `docs/process/v5-artifact-flow.md:3,10-17` |
| A20 | Added prospective to glossary | 12–13 | `docs/contracts/analysis_plans.md:69-103` |
| A21 | Added admitted to glossary | 14–15 | `docs/contracts/analysis_plans.md:334-355` |
| A22 | Added gate to glossary | 16–17 | `docs/process/state_kernel.json:4533-4719` |
| A23 | Added governed to glossary | 18–19 | `docs/orchestration.md:1-75` |
| A24 | Replaced producer with concrete generating programs | 168–169, 481 | `docs/process/v5-artifact-flow.md:19-25` |
| A25 | Replaced “three-seat” with three independent reviewers | 634–635 | `docs/decision_log.md:192` |
| A26 | Explained the no-agent quiet-machine condition physically | 571 | `docs/process/state_kernel.json:4718-4719` |
| A27 | Explained unmatched as never collected in matched pairs | 218–222 | `docs/process_traces/2026-07-17-exploratory-block/results.md:3-8` |
| A28 | Built the two-clock time-anchor defect at first use | 174–178 | `docs/decision_log.md:4159-4174` |
| B1 | Restored exact `0.29-0.49 J` on `~50 J` range | 179–181 | `docs/decision_log.md:4723-4727` |
| B2 | Added floor plus claim-side bound `(~5 J for phase contrasts)` disclosure | 182–185 | `docs/decision_log.md:4768-4779` |
| B3 | Dropped “fifth”; described regeneration under the new pair | 75–77 | `docs/decision_log.md:191` |
| B4 | Softened reviewer provenance to blind separate sessions across more than one vendor | 159–162 | `00-MAGISTRATE-SYNTHESIS.md:3-8`; Opus review `:80` |

## Glossary first-use table

Every glossary term is first defined in the glossary and appears at least once again.

| Term | First-use line | Total uses |
|---|---:|---:|
| Frozen | 10 | 14 |
| Prospective | 12 | 8 |
| Admitted | 14 | 4 |
| gate | 16 | 15 |
| Governed | 18 | 10 |
| measurement window | 20 | 2 |
| run bundle | 21 | 6 |
| pack | 23 | 15 |
| detection floor | 25 | 2 |
| mint | 27 | 7 |
| arm | 29 | 5 |
| verdict | 30 | 5 |
| refusal | 31 | 9 |
| cell | 32 | 6 |
| component | 33 | 5 |
| state kernel | 35 | 2 |
| manifest | 36 | 4 |
| Strict validation | 38 | 5 |
| Finalization | 39 | 5 |
| results fill | 41 | 4 |
| transaction | 44 | 4 |
| Telemetry | 45 | 12 |
| tokenizer | 47 | 3 |

## Verification commands and tails

```text
$ python3 -m unittest tests.test_paper_terms_lint tests.test_gen_state
...........................................
----------------------------------------------------------------------
Ran 43 tests in 1.903s

OK
```

```text
$ git diff --check
(no output; exit 0)
```

Report-38 loop, rerun exactly:

```zsh
missing_count=0
while IFS= read -r path; do
  if [[ ! -e "$path" ]]; then
    print -r -- "missing: $path"
    missing_count=$((missing_count + 1))
  fi
done < <(rg -o '`[^`]+`' PROJECT_STATUS.md | tr -d '`' | rg '^[A-Za-z0-9_.-]+/' | rg -v '^github[.]com/')
if (( missing_count == 0 )); then
  print 'all PROJECT_STATUS repository pointers resolve'
else
  exit 1
fi
```

Tail:

```text
all PROJECT_STATUS repository pointers resolve
```

Glossary audit command and final tail:

```text
$ terms=$(sed -n '/Plain-language terms used throughout:/,/Freshness and authority:/p' PROJECT_STATUS.md | rg -o '\*[^*]+\*' | tr -d '*' | awk '!seen[tolower($0)]++'); bad=0; while IFS= read -r term; do first=$(rg -n -i -m1 -F -- "$term" PROJECT_STATUS.md); count=$(rg -i -o -F -- "$term" PROJECT_STATUS.md | wc -l | tr -d ' '); first_line=$(printf '%s' "$first" | cut -d: -f1); printf '%s | first %s | uses %s\n' "$term" "$first_line" "$count"; if (( count < 2 )); then bad=1; fi; done <<< "$terms"; exit "$bad"
transaction | first 44 | uses 4
Telemetry | first 45 | uses 12
tokenizer | first 47 | uses 3
```

```text
$ git diff --stat
 PROJECT_STATUS.md | 263 ++++++++++++++++++++++++++++++++++--------------------
 1 file changed, 166 insertions(+), 97 deletions(-)
```