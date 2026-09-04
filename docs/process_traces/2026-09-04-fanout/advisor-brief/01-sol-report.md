```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Refreshed the one-page Rivoire advisor brief around the live Qwen3 campaign, metrology checks, printed negative result, and three judgment questions.",
  "workspace": {"base_requested":null,"base_mode":null,"head_start":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","head_end":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","upstream_end":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","branch":"feat/2026-09-04-advisor-brief-refresh"},
  "pathspec": ["docs/advisor_briefs/2026-09-advisor-brief.md","docs/process_traces/2026-09-04-fanout/advisor-brief/01-sol-report.md"],
  "unowned_dirty": [],
  "verdict": {"implementation":"implemented","acceptance":"ready"},
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"awk '$0==\"<!-- BEGIN FIRST_USE_CHECK -->\"{f=1;next}$0==\"<!-- END FIRST_USE_CHECK -->\"{f=0} f && !/^```/{print}' docs/process_traces/2026-09-04-fanout/advisor-brief/01-sol-report.md | python3","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["FIRST_USE_PASS sentences=45 terms=25 questions=3 forbidden_hits=0"]},"expected":{"exit_code":0,"tail_regex":"^FIRST_USE_PASS sentences=45 terms=25 questions=3 forbidden_hits=0$"}},
    {"id":"V2","kind":"inspection","cmd":"git diff --check && awk '$0==\"<!-- BEGIN BRIEF_STRUCTURE_CHECK -->\"{f=1;next}$0==\"<!-- END BRIEF_STRUCTURE_CHECK -->\"{f=0} f && !/^```/{print}' docs/process_traces/2026-09-04-fanout/advisor-brief/01-sol-report.md | python3","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["BRIEF_STRUCTURE_PASS questions=3 word_count=773 links=5 missing_links=0 forbidden_hits=0"]},"expected":{"exit_code":0,"tail_regex":"^BRIEF_STRUCTURE_PASS questions=3 word_count=773 links=5 missing_links=0 forbidden_hits=0$"}},
    {"id":"V3","kind":"inspection","cmd":"awk '$0==\"<!-- BEGIN SOURCE_TRACE_CHECK -->\"{f=1;next}$0==\"<!-- END SOURCE_TRACE_CHECK -->\"{f=0} f && !/^```/{print}' docs/process_traces/2026-09-04-fanout/advisor-brief/01-sol-report.md | python3","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["SOURCE_TRACE_PASS campaign=6 dependence=4 excursion=5 registry=5 paper_branch=4"]},"expected":{"exit_code":0,"tail_regex":"^SOURCE_TRACE_PASS campaign=6 dependence=4 excursion=5 registry=5 paper_branch=4$"}},
    {"id":"V4","kind":"inspection","cmd":"awk '$0==\"<!-- BEGIN REPORT_CONTRACT_CHECK -->\"{f=1;next}$0==\"<!-- END REPORT_CONTRACT_CHECK -->\"{f=0} f && !/^```/{print}' docs/process_traces/2026-09-04-fanout/advisor-brief/01-sol-report.md | python3","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["REPORT_CONTRACT_PASS schema=claude-codex-report/v1 pathspec=2 scope_clean=true"]},"expected":{"exit_code":0,"tail_regex":"^REPORT_CONTRACT_PASS schema=claude-codex-report/v1 pathspec=2 scope_clean=true$"}}
  ],
  "flags": []
}
```

## Change

Replaced the stale advisor-facing campaign account with a 773-word brief for
Suzanne Rivoire. It translates the live fifth-generation Qwen3 design into
plain language, defines the dominance test physically, distinguishes the two
supporting metrology analyses, states the diagnostic negative result without
overclaiming, and ends with exactly the three requested questions. Older briefs
were not modified.

### Finding and decision table

| Finding | Evidence | Decision in the brief |
|---|---|---|
| The earlier meeting material names the superseded Qwen2.5 pair and fixed 256-token prompt. | Issued campaign rulings for the current fifth-generation configuration. | Name Qwen3-1.7B versus Qwen3-8B, explain the pre-collection prompt-selection trial, and state that no campaign result is claimed yet. |
| The old coded dominance label was not a meaningful falsifier. | The adopted ratio criterion requires boundary-moved versus point-only bounds to have R ≥ 2 for every required component and condition; the comparative shared-error ratio can withdraw the sentence. | Define both ratios through the physical movement of phase boundaries and the error that repetitions cannot average away. |
| Ten paired blocks need not be independent merely because the order counters linear drift. | The dependence sheet fixes independent, estimated-neighbour-correlation, and effective-sample-halving analyses. | Explain that only repeat uncertainty changes and disagreement withholds direction; agreement is not proof of independence. |
| The 30.07-millisecond calibration bound mixes systematic and variable effects. | The issued decomposition gives 13.0, 14.0, 1.93, and 1.13 milliseconds for its four terms. | State that onset bias is the largest single term but worst-pulse scatter is slightly larger, then label the GPU-ramp account as untested interpretation. |
| The manuscript's negative result is easy to misread as zero prompt-processing energy. | Section 6 on the specified paper branch and issued registry records show 37 of 50 phases with two overlaps and 13 with three. | State that the finding is a sampling-support refusal from an earlier diagnostic population, not a model comparison or current-campaign limitation. |
| The requested advisor decisions are transfer, multiplicity, and cadence. | Mission prompt. | End with exactly three questions, one on each topic. |

## Executed evidence

### V1 — mechanical first-use and visible-shorthand check

Replay command:

```sh
awk '$0=="<!-- BEGIN FIRST_USE_CHECK -->"{f=1;next}$0=="<!-- END FIRST_USE_CHECK -->"{f=0} f && !/^```/{print}' docs/process_traces/2026-09-04-fanout/advisor-brief/01-sol-report.md | python3
```

<!-- BEGIN FIRST_USE_CHECK -->
```python
from pathlib import Path
import re
path = Path('docs/advisor_briefs/2026-09-advisor-brief.md')
text = path.read_text(encoding='utf-8')
term_rules = [
 ('prompt processing', 'glossed', 'when a model reads a prompt'),
 ('token generation', 'glossed', 'when it produces later output tokens'),
 ('power sampler', 'built', 'reports average power over intervals'),
 ('phase boundary', 'built', 'can move energy from one phase to the other'),
 ('claim-bearing campaign', 'glossed', 'meaning the campaign eligible to support'),
 ('four-bit models', 'glossed', 'weights stored with four bits per value'),
 ('frozen campaign configuration', 'glossed', 'fixed and sealed against later change'),
 ('conversation template', 'glossed', 'the format that turns a conversation into model input'),
 ('greedy decoding', 'glossed', 'selects the most likely next token'),
 ('shakedown', 'glossed', 'an instrument-readiness trial'),
 ('power-sampling records', 'glossed', 'an average-power report for a recorded interval'),
 ('A/B/B/A blocks', 'glossed', 'one smaller-model run, two larger-model runs'),
 ('dominance ratio', 'glossed', 'divides the worst allowed false difference'),
 ('false difference', 'glossed', 'an apparent condition difference that timing uncertainty could create'),
 ('components', 'glossed', 'same-model repeatability and the between-model comparison'),
 ('shared-error ratio', 'built', 'moves the session-wide timing error in one shared direction'),
 ('dependence sensitivity sheet', 'built', 'asks whether adjacent blocks move together'),
 ('effective sample', 'glossed', 'the smaller number of independent blocks'),
 ('direction screen', 'glossed', 'requires the complete uncertainty interval'),
 ('timing-excursion decomposition', 'built', 'explains the retained'),
 ('calibration bound', 'glossed', 'the maximum timing displacement carried into the energy calculation'),
 ('onset bias', 'built-before', 'repeatable start-delay'),
 ('transfer fiducial', 'glossed', 'a known event used to test that transfer'),
 ('Holm family', 'glossed', 'a step-down correction controlling'),
 ('cadence', 'built-same-sentence', 'sampling intervals near a tenth of a second'),
]
visible = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', text)
blocks = []
for block in re.split(r'\n\s*\n', visible):
    block = block.strip()
    if not block or block.startswith('#'):
        continue
    blocks.append(re.sub(r'\n(?!\d+\. )', ' ', block))
sentences = []
for block in blocks:
    sentences.extend(s.strip() for s in re.split(r'(?<=[.!?])\s+(?=(?:\*\*|[A-Z0-9]))', block) if s.strip())
seen, rows = set(), []
for i, sentence in enumerate(sentences, 1):
    first = []
    low = sentence.lower().replace('**', '')
    for term, status, evidence in term_rules:
        if term.lower() in low and term not in seen:
            if evidence.lower() not in low and status != 'built-before':
                raise SystemExit(f'FAIL sentence {i}: {term!r} lacks first-use evidence {evidence!r}')
            seen.add(term)
            first.append(f'{term} — {status}')
    excerpt = re.sub(r'\s+', ' ', sentence).replace('|', '/')
    if len(excerpt) > 72:
        excerpt = excerpt[:69] + '…'
    rows.append((i, excerpt, '; '.join(first) or 'none; plain language or previously built', 'PASS'))
missing = [term for term, _, _ in term_rules if term not in seen]
if missing:
    raise SystemExit('FAIL unaudited terms: ' + ', '.join(missing))
forbidden = [r'\bD-\d{3}\b', r'registry row', r'kernel row', r'`_v\d+`', r'\bp256\b']
hits = [pattern for pattern in forbidden if re.search(pattern, visible, re.I)]
if hits:
    raise SystemExit('FAIL internal shorthand: ' + ', '.join(hits))
if visible.count('?') != 3:
    raise SystemExit(f"FAIL question count: {visible.count('?')}")
print('| Sentence | Opening text | First-use disposition | Result |')
print('|---:|---|---|---|')
for row in rows:
    print(f'| {row[0]} | {row[1]} | {row[2]} | {row[3]} |')
print(f'FIRST_USE_PASS sentences={len(sentences)} terms={len(term_rules)} questions=3 forbidden_hits=0')
```
<!-- END FIRST_USE_CHECK -->

Output table, pasted in full:

| Sentence | Opening text | First-use disposition | Result |
|---:|---|---|---|
| 1 | JouleWise measures the energy an Apple-silicon laptop assigns to **pr… | prompt processing — glossed; token generation — glossed | PASS |
| 2 | The metrology problem is timing: the power sampler reports average po… | power sampler — built; phase boundary — built | PASS |
| 3 | The **claim-bearing campaign**, meaning the campaign eligible to supp… | claim-bearing campaign — glossed; four-bit models — glossed | PASS |
| 4 | This fifth frozen campaign configuration has rules fixed and sealed a… | frozen campaign configuration — glossed | PASS |
| 5 | It replaces the earlier Qwen2.5 comparison and fixed 256-token prompt. | none; plain language or previously built | PASS |
| 6 | Token generation uses real prompts, the Qwen3 **conversation template… | conversation template — glossed; greedy decoding — glossed | PASS |
| 7 | A **shakedown**, an instrument-readiness trial, selects the shortest … | shakedown — glossed; power-sampling records — glossed | PASS |
| 8 | The two comparisons are prompt processing and token generation. | none; plain language or previously built | PASS |
| 9 | Each uses ten complete **A/B/B/A blocks**: one smaller-model run, two… | A/B/B/A blocks — glossed | PASS |
| 10 | This order counters simple linear drift. | none; plain language or previously built | PASS |
| 11 | No campaign result is claimed here; these are its fixed judging rules. | none; plain language or previously built | PASS |
| 12 | Issued campaign design | none; plain language or previously built | PASS |
| 13 | The main falsification test asks whether timing attribution dominates… | none; plain language or previously built | PASS |
| 14 | For each model and phase, the **dominance ratio**, R, divides the wor… | dominance ratio — glossed; false difference — glossed | PASS |
| 15 | Its components are same-model repeatability and the between-model com… | components — glossed | PASS |
| 16 | Timing is dominant only if R ≥ 2 for every component and condition: b… | none; plain language or previously built | PASS |
| 17 | A **shared-error ratio** instead moves the session-wide timing error … | shared-error ratio — built | PASS |
| 18 | If it is below two, the paper withdraws the dominance sentence. | none; plain language or previously built | PASS |
| 19 | This separates timing error that repeats cannot average away from ind… | none; plain language or previously built | PASS |
| 20 | Issued dominance criterion | none; plain language or previously built | PASS |
| 21 | The **dependence sensitivity sheet** asks whether adjacent blocks mov… | dependence sensitivity sheet — built | PASS |
| 22 | It recomputes each comparison with independent blocks, estimated neig… | effective sample — glossed | PASS |
| 23 | Only repeat uncertainty changes; issued measurement uncertainty remai… | none; plain language or previously built | PASS |
| 24 | Agreement does not prove independence. | none; plain language or previously built | PASS |
| 25 | Disagreement prints all three intervals and withholds the direction. | none; plain language or previously built | PASS |
| 26 | The **direction screen** requires the complete uncertainty interval t… | direction screen — glossed | PASS |
| 27 | Pre-registered dependence analysis | none; plain language or previously built | PASS |
| 28 | The **timing-excursion decomposition** explains the retained 30.07-mi… | timing-excursion decomposition — built; calibration bound — glossed | PASS |
| 29 | Its terms are 13.0 milliseconds of median, repeatable start-delay; 14… | none; plain language or previously built | PASS |
| 30 | The repeatable onset bias is the largest single term, but pulse-to-pu… | onset bias — built-before | PASS |
| 31 | Removing the bias would greatly improve a typical edge while shrinkin… | none; plain language or previously built | PASS |
| 32 | A plausible but untested explanation is that starting graphics work r… | none; plain language or previously built | PASS |
| 33 | Issued decomposition and source artifact | none; plain language or previously built | PASS |
| 34 | A sampling record counts only when its interval overlaps prompt proce… | none; plain language or previously built | PASS |
| 35 | In the retained earlier diagnostic population, 37 of 50 phases overla… | none; plain language or previously built | PASS |
| 36 | Most were therefore too brief for this phase-energy calculation. | none; plain language or previously built | PASS |
| 37 | That does not mean their energy was zero, compare models, or limit th… | none; plain language or previously built | PASS |
| 38 | It explains the current five-record prompt-selection requirement. | none; plain language or previously built | PASS |
| 39 | The source is the issued result records, also printed in manuscript S… | none; plain language or previously built | PASS |
| 40 | 1. | none; plain language or previously built | PASS |
| 41 | Does an independently time-stamped no-work gap inside real inference … | transfer fiducial — glossed | PASS |
| 42 | 2. | none; plain language or previously built | PASS |
| 43 | Do prompt processing and token generation belong in one two-compariso… | Holm family — glossed | PASS |
| 44 | 3. | none; plain language or previously built | PASS |
| 45 | Given sampling intervals near a tenth of a second and the three-recor… | cadence — built-same-sentence | PASS |

Tail: `FIRST_USE_PASS sentences=45 terms=25 questions=3 forbidden_hits=0`

### V2 — one-page structure, links, and exact question count

<!-- BEGIN BRIEF_STRUCTURE_CHECK -->
```python
from pathlib import Path
import re
p = Path('docs/advisor_briefs/2026-09-advisor-brief.md')
s = p.read_text(encoding='utf-8')
visible = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', s)
questions = re.findall(r'^\d+\. .*\?$', s, re.M)
assert len(questions) == 3
assert visible.count('?') == 3
assert not re.search(r'\bD-\d{3}\b|registry row|kernel row|`_v\d+`|\bp256\b', visible, re.I)
words = len(s.split())
assert words <= 900
links = re.findall(r'\[[^]]+\]\(([^)#]+)(?:#[^)]+)?\)', s)
missing = [link for link in links if not (p.parent / link).resolve().exists()]
assert not missing
print(f'BRIEF_STRUCTURE_PASS questions=3 word_count={words} links={len(links)} missing_links=0 forbidden_hits=0')
```
<!-- END BRIEF_STRUCTURE_CHECK -->

Tail: `BRIEF_STRUCTURE_PASS questions=3 word_count=773 links=5 missing_links=0 forbidden_hits=0`

### V3 — claim-to-source trace

<!-- BEGIN SOURCE_TRACE_CHECK -->
```python
from pathlib import Path
import subprocess
checks = {
 'campaign': (Path('docs/decision_log.md').read_text(), ['Qwen3-1.7B-4bit', 'Qwen3-8B-4bit', 'generation `_v5`', 'forced 512', 'R ≥ 2', 'Holm family stays m = 2']),
 'dependence': (Path('docs/paper/round7/dependence-sensitivity.md').read_text(), ['Registered composition with', 'AR(1) estimated-adjacency model', 'Fixed effective-n halving', 'dependence changes only the repeat component']),
 'excursion': (Path('docs/paper/round7/excursion-decomposition.md').read_text(), ['30.067932', '13.000000', '14.000000', '1.932935', '1.134997']),
 'registry': (Path('docs/paper/results-fill-registry.md').read_text(), ['| DG-066', '| DG-067', '| DG-069', '| DG-076', '| DG-077']),
}
branch = subprocess.check_output(['git', 'show', 'origin/feat/2026-09-02-paper-e:docs/paper/draft-v2-skeleton.md'], text=True)
checks['paper_branch'] = (branch, ['## 6. Demonstration results', '### Printed negative result: short prompt processing has too few overlapping records', '37 of 50 phases', 'remaining 13 of 50'])
for name, (body, needles) in checks.items():
    missing = [needle for needle in needles if needle not in body]
    assert not missing, (name, missing)
print('SOURCE_TRACE_PASS campaign=6 dependence=4 excursion=5 registry=5 paper_branch=4')
```
<!-- END SOURCE_TRACE_CHECK -->

Tail: `SOURCE_TRACE_PASS campaign=6 dependence=4 excursion=5 registry=5 paper_branch=4`

### V4 — report contract, write scope, and older-brief preservation

<!-- BEGIN REPORT_CONTRACT_CHECK -->
```python
from pathlib import Path
import json, re, subprocess
report = Path('docs/process_traces/2026-09-04-fanout/advisor-brief/01-sol-report.md')
text = report.read_text(encoding='utf-8')
assert text.startswith('```json\n')
assert len(re.findall(r'^```json$', text, re.M)) == 1
match = re.match(r'^```json\n(.*?)\n```(?:\n|$)', text, re.S)
assert match
payload = json.loads(match.group(1))
assert payload['schema'] == 'claude-codex-report/v1'
expected = {
 'docs/advisor_briefs/2026-09-advisor-brief.md',
 'docs/process_traces/2026-09-04-fanout/advisor-brief/01-sol-report.md',
}
assert set(payload['pathspec']) == expected
status = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'], text=True).splitlines()
paths = {line[3:] for line in status}
assert paths == expected, (paths, expected)
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == payload['workspace']['head_end']
print('REPORT_CONTRACT_PASS schema=claude-codex-report/v1 pathspec=2 scope_clean=true')
```
<!-- END REPORT_CONTRACT_CHECK -->

Tail: `REPORT_CONTRACT_PASS schema=claude-codex-report/v1 pathspec=2 scope_clean=true`

## Verification notes

No test module was touched or named. Per the mission's preflight rule, the
repository-wide unit-test suite was not run; verification was limited to the
focused document, provenance, first-use, report-contract, and write-scope
inspections above. The first combined provenance grep used an invalid ripgrep
escape and produced no evidence; V3 is the corrected, passing source trace.
The first V1–V4 replay used loose marker matches that selected command strings
from the envelope instead of the embedded scripts, so all four invocations
failed before running a check; exact-line marker matching corrected that
extractor. The first corrected V4 then counted its own ` ```json ` source
literal as a second fence; the final check counts only complete fence lines.
Its next attempt split on backticks embedded inside a JSON command; the final
parser matches complete opening and closing fence lines instead.
The following scope check initially saw Git's collapsed untracked-directory
display; the final command requests every untracked file before comparing the
two exact paths.
