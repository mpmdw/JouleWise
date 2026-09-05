```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"partial",
  "summary":"F1 closed; NOT LANDABLE: paper-K registry conflict; fetch blocked.",
  "workspace":{"base_requested":"3aeed4ed","base_mode":"exact","head_start":"3aeed4ed985cffbf6553cc0983870aae31637aef","head_end":"3aeed4ed985cffbf6553cc0983870aae31637aef","upstream_end":"3aeed4ed985cffbf6553cc0983870aae31637aef","branch":"feat/2026-09-05-d166-prompt0"},
  "pathspec":["docs/process_traces/2026-09-05-d166-prompt0/05-delta-round-1.md"],
  "unowned_dirty":[],
  "verdict":{"landing":"NOT LANDABLE","F1":"closed against cached paper-K","findings":[{"id":"F2","severity":"blocker","path":"docs/paper/results-fill-registry.md","text":"Both branches edit V5-WL-001 and V5-WL-004; merge-tree reports a content conflict."}]},
  "verification":[
    {"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_d117_contrast_v5_pack","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 44 tests in 15.331s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 10 tests in 1.726s","","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V3","kind":"inspection","cmd":"PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 scripts/check_paper_round7_artifacts.py --literals-only --corpus-root /Users/edr/code/JouleWise","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["R7F PLACED 0/16","R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"MISMATCHES 0"}},
    {"id":"V4","kind":"other","cmd":"git fetch origin feat/2026-09-04-paper-k","cwd":".","observed":{"result":"fail","exit_code":255,"tail":["error: cannot open '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-d166-prompt0/FETCH_HEAD': Operation not permitted"]},"expected":{"exit_code":0,"tail_regex":".*"}},
    {"id":"V5","kind":"inspection","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport os, subprocess, tempfile\nfrom pathlib import Path\nobjects = subprocess.check_output(['git','rev-parse','--git-path','objects'],text=True).strip()\nwith tempfile.TemporaryDirectory(prefix='d166-merge-') as scratch:\n env = dict(os.environ, GIT_OBJECT_DIRECTORY=scratch, GIT_ALTERNATE_OBJECT_DIRECTORIES=str(Path(objects).resolve()))\n p = subprocess.run(['git','merge-tree','origin/feat/2026-09-04-paper-k','HEAD'],env=env,text=True,capture_output=True)\n print(p.stdout, end=''); print(p.stderr,end=''); print('MERGE_EXIT='+str(p.returncode))\nPY","cwd":".","observed":{"result":"fail","exit_code":0,"tail":["Auto-merging docs/paper/results-fill-registry.md","CONFLICT (content): Merge conflict in docs/paper/results-fill-registry.md","MERGE_EXIT=1"]},"expected":{"exit_code":0,"tail_regex":"MERGE_EXIT=0"}}
  ],
  "flags":[{"id":"E1","kind":"environment","level":"blocking","text":"Shared Git metadata is outside the writable sandbox; fetch failed. Paper-K inspection and merge use cached 3d1ab23b8023a75450354579b032818225e62ea5.","needs":"Lead fetches paper-K and repeats the integration check after resolving F2."}]
}
```

## Findings

**F2 — blocker.** The cached paper-K merge conflicts only in
`docs/paper/results-fill-registry.md`, at the two workload rows. Preserve this
fix's rule IDs, supersession authority, exact disclaimer and destination while
retaining paper-K's clarification that same-model floor packs remain unchanged.
Lead must resolve and recheck. Direct merge-tree exited 128 (object creation
denied). V5 used temporary objects: child exit 1, wrapper 0. Checkout, index
and refs stayed unchanged.

F1 closed: refuter 03, fix 04 and `git show 3aeed4ed` inspected.
Rows 146/149 have five cells and KEY_FROZEN status. Both name
`d166_fixed_prompt_zero.v1`, `d166_block_prompt_cycle.v1`, the exact ruling-43
path and Q-17-4. V5-WL-004 contains exactly: “The comparison supports this fixed
prompt and makes no prompt-population generality claim.” Census lines 163–168
name the Section 1 workload destination. Cached paper-K places that sentence
at draft-v2-skeleton.md:196–197, wrapped across two lines in Section 1's workload
paragraph; whitespace-normalized wording is exact.

## Residual risk

No standing parser/test found validates these rows: the round-7 parser at
scripts/check_paper_round7_artifacts.py:236 reads DX rows; the renderer at
scripts/render_results_fills.py:100 reads bracketed token rows. Both were run
and exclude V5-WL-001/004. Separate assertions checked grammar and wording.
V3 covers literals only. Required modules ran
sequentially; no discovery suite, agent launcher or hardware collection ran.
