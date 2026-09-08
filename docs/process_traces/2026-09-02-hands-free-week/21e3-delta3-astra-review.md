```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"partial",
  "summary":"D1/D2/D4/D5 pass; literal D3/D6 fail on unchanged text. Delta R3 passes, older timestamp signatures survive, and required mktemp benches are sandbox-blocked.",
  "workspace":{"base_requested":"f712d0c9","base_mode":"descendant","head_start":"a2be9591954c607c3505ffa4c25559a30519d94a","head_end":"a2be9591954c607c3505ffa4c25559a30519d94a","upstream_end":"a2be9591954c607c3505ffa4c25559a30519d94a","branch":"bookkeeping/2026-09-08-activation-evidence"},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"findings":[{"id":"E1","severity":"should_fix","summary":"Pre-existing event-time claims lack same-line sources; activation IDs also produce false negatives in R3."}]},
  "verification":[
    {
      "id":"V1","kind":"inspection",
      "cmd":"python3 -B -c 'import pathlib,re,subprocess as S\np=pathlib.Path(\"docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-arm-plan.md\");s=p.read_text()\nbs=list(re.finditer(r\"^\\x60{3}zsh\\n(.*?)^\\x60{3}$\",s,re.M|re.S));assert len(bs)==3\nfor i,b in enumerate(bs):\n r=S.run([\"zsh\",\"-n\"],input=b[1],text=True,capture_output=True);print(\"zsh\",i,r.returncode,repr(r.stdout+r.stderr))\ncs=re.findall(\"<<\"+chr(39)+\"PY\"+chr(39)+r\"[^\\n]*\\n(.*?)^PY$\",s,re.M|re.S)\nfor i,c in enumerate(cs):compile(c,str(i),\"exec\")\nprint(\"compiled PY:\",len(cs))\nb=bs[2][1];rows=list(enumerate(b.splitlines(),s.count(\"\\n\",0,bs[2].start())+2));q=chr(34)\nget=lambda t:[(i,l) for i,l in rows if t in l]\nh=get(\"un-publishing the plan this session authored\");plan=\"--plan \"+q+\"$NIGHT_CUSTODY/night_plan.json\"+q+\" --hour 2 --minute 56\"\nprint(\"D1\",s.count(\"un-publishing the plan this session authored\"),h[0][0],plan in h[0][1],(\"|| { print \"+q+\"ABORT: agent install failed\"+q+\"; exit 1; }\") in bs[0][1])\nd=get(\"date +%s\");me=get(\"me = json.load\")[0][0];mk=get(\"mkdir -p\")[0][0]\nprint(\"D2\",b.count(\"date +%s\"),d[0][0],\"-lt 1788945300\" in d[0][1],me,mk)\nr=S.run([\"grep\",\"-nE\",\"02:00|16456\",str(p)],capture_output=True,text=True);print(\"D3\",r.returncode,r.stdout.strip())\nfor t in [\"standdown.request\",\"night_plan.json(N)\"]:\n f=get(t);print(\"D4\",t,b.count(t),f[0][0],f[0][0]<me,bool(re.search(r\"\\|\\| \\{ print \\\"ABORT: [^\\\"]+\\\"; exit 1; \\} # D4$\",f[0][1])))\nl=h[0][1];print(\"D5\",l.index(\"--uninstall\"),l.index(\"rm -f \"+q+\"$NIGHT_CUSTODY/night_plan.json\"+q),plan+\" --uninstall\" in l)\nnorm=lambda rev:S.run([\"tr\",\"-s\",\"[:space:]\",\" \"],input=S.check_output([\"git\",\"show\",rev+\":docs/process/NIGHT_HANDBACK.md\"]),capture_output=True).stdout\nprint(\"D6 word-identity\",norm(\"f712d0c9\")==norm(\"a2be9591\"))\nr=S.run([\"awk\",\"length>110\",\"docs/process/NIGHT_HANDBACK.md\"],capture_output=True,text=True);print(\"D6 awk\",r.returncode,repr(r.stdout))\n'",
      "cwd":".",
      "observed":{"result":"fail","exit_code":0,"tail":["D1 1 277 True True","D2 1 248 True 257 273","D4 standdown.request 1 249 True True","D4 night_plan.json(N) 1 250 True True","D5 318 339 True","D6 word-identity True","D6 awk 0 '`scripts/install_night_agent.sh --plan /Users/edr/night-custody/rehearsal-20260909/night_plan.json --hour 2 --minute 56 --uninstall`\\n'"]},
      "expected":{"exit_code":0,"tail_regex":"D6 awk 0 ''"}
    },
    {
      "id":"V2","kind":"inspection",
      "cmd":"python3 -B -c 'import pathlib,re,subprocess\nr=pathlib.Path(\"docs/process_traces/2026-09-02-hands-free-week\")\nt=re.compile(r\"[0-9]{1,2}:[0-9]{2}\")\na=re.compile(r\"\\b[0-9a-f]{8}\\b|internalDate [0-9]{10}|epoch_s|\\b17[0-9]{8}\\b|events\\.jsonl|(pass[0-9]|bench)-[A-Za-z0-9._-]+\")\nd=subprocess.check_output([\"git\",\"diff\",\"-U0\",\"f712d0c9..a2be9591\",\"--\",\"docs/\"],text=True)\nbad=[l for l in d.splitlines() if l.startswith(\"+\") and not l.startswith(\"+++\") and t.search(l) and not a.search(l)]\nprint(\"delta:\",len(bad));print(*bad,sep=\"\\n\") if bad else None\nfor n in [\"21b-rehearsal-20260909-arm-plan.md\",\"21-first-launchd-activation-1ef89702.md\"]:\n bad=[i for i,l in enumerate((r/n).read_text().splitlines(),1) if t.search(l) and not a.search(l)]\n print(n,bad)\n'",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["delta: 0","21b-rehearsal-20260909-arm-plan.md [31, 35, 42, 81, 120, 138, 147, 163, 164, 280]","21-first-launchd-activation-1ef89702.md [1, 3, 6, 18, 19, 32, 52, 53, 59, 61, 69, 70]"]},
      "expected":{"exit_code":0,"tail_regex":"delta: 0"}
    },
    {
      "id":"V3","kind":"test","cmd":"mktemp -d /private/tmp/pr295-delta3.XXXXXX","cwd":".",
      "observed":{"result":"fail","exit_code":1,"tail":["mktemp: mkdtemp failed on /private/tmp/pr295-delta3.pXyA5S: Operation not permitted"]},
      "expected":{"exit_code":0,"tail_regex":"/private/tmp/pr295-delta3\\."}
    },
    {
      "id":"V4","kind":"test","cmd":"zsh scripts/install_night_agent.sh --uninstall --plan /dev/null/pr295-absent-plan.json --hour 2 --minute 56","cwd":".",
      "observed":{"result":"pass","exit_code":2,"tail":["plan not found: /dev/null/pr295-absent-plan.json"]},
      "expected":{"exit_code":2,"tail_regex":"plan not found:"}
    }
  ],
  "flags":[
    {"id":"ENV1","kind":"verification_gap","level":"blocking","text":"Read-only sandbox denied mktemp. Stdin syntax checks and in-memory benches ran; required file-backed benches did not.","needs":"Lead reruns the prescribed benches with scratch-write permission."},
    {"id":"A1","kind":"lead_ruling","level":"nonblocking","text":"Literal D3 and D6 fail on unchanged historical/window and command text; neither demonstrates a new operational defect.","needs":"Disposition the literal acceptance mismatches."}
  ]
}
```

## Findings

**E1 — should_fix, predates this delta:** the hand-typed event-time signature survives in the whole documents. Examples include trace 21’s lid-opening `~00:40`, work-start `00:52`, and acceptance `~00:57` claims. Some other flagged times have evidence elsewhere but lack the required same-line token. Cure: attach the supporting primary source on each event line, or delete the unsupported time.

Below, `21b` means `21b-rehearsal-20260909-arm-plan.md`; `21` means `21-first-launchd-activation-1ef89702.md`, both under `docs/process_traces/2026-09-02-hands-free-week/`.

**§3 verification**

V1 contains the exact replay command for extraction, compilation, and D1–D6.

| Check | Result | Exact output / interpretation |
|---|---|---|
| Three zsh blocks | PASS | Fences `77..121`, `161..227`, `242..281`; `zsh 0 0 ''`, `zsh 1 0 ''`, `zsh 2 0 ''`. Parsed through stdin because scratch writes were denied. |
| Every PY heredoc | PASS | `compiled PY: 4`; all four passed `compile(..., "exec")`. |
| D1 | PASS | `D1 1 277 True True`: one occurrence, inside B, required plan arguments present; historical block has bare fatal guard. |
| D2 | PASS | `D2 1 248 True 257 273`: one clock read; upper bound present; guard precedes lock read and custody mkdir. |
| D3 | **FAIL literally** | `grep -nE '02:00\|16456'` returns only line 81, ending `now < 2026-09-09 02:00 PDT.` No pass3 citation there. This is an unchanged historical bound, not the removed observation. |
| D4 | PASS | `D4 standdown.request 1 249 True True`; `D4 night_plan.json(N) 1 250 True True`. Both precede line 257 and have fatal guards, followed by `# D4`. |
| D5 | PASS | `D5 318 339 True`: zero-based uninstall index 318 precedes rm index 339; uninstall carries plan/hour/minute. |
| D6 identity | PASS | Both `git show … \| tr -s '[:space:]' ' '` results are identical: `D6 word-identity True`. |
| D6 width | **FAIL literally** | `awk 'length>110' docs/process/NIGHT_HANDBACK.md` prints the uninstall command shown in V1. Line 71 is 132 characters at **both** base and head. Changed prose passes the width limit. |

The replacement D3 citation resolves:

```text
git ls-files --error-unmatch docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/pass3-process-tree-keepalive.txt
→ rc 0
git cat-file -e f9205c49:docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/pass3-process-tree-keepalive.txt
→ rc 0
```

The artifact is a byte-identical rename of the base’s process-tree capture.

**R3 results**

Delta gate: **PASS, zero violating added lines**. Whole-file gate: **10 lines in 21b; 12 in trace 21**. Exact Python regex and replay command are V2.

Every lexical rejection is listed below; seconds are retained where present.

| Class | Location | Times without an R3-accepted same-line token |
|---|---|---|
| Event record | 21b:31 | `01:05:21`, `01:10:44`, `01:10:59` |
| Event record | 21b:35 | `02:03` |
| Window bound | 21b:42 | `01:56` |
| Historical bound | 21b:81 | `02:00` |
| Window constants | 21b:120 | `02:31`, `02:40`, `02:41`, `02:45`, `03:30` |
| Scheduled target in quoted email | 21b:138 | `02:56` |
| Courier deadline | 21b:147 | `03:16` |
| Window bounds | 21b:163 | `01:56`, `02:15` |
| Request boundary | 21b:164,280 | `02:31` on each line |
| Event record | 21:1 | `00:51:55` |
| Historical section locator | 21:3 | `~20:15` |
| Census record | 21:6 | `00:55` |
| Event record | 21:18 | `~00:40` |
| Artifact observation | 21:19 | `00:57:27` |
| Census record | 21:32 | `00:55` |
| Event records | 21:52,53,59 | `00:46:54`, `00:52`, `~00:57`, respectively |
| Expected availability bound | 21:61 | `02:30` |
| Artifact observation | 21:69 | `00:39:32` |
| Process start record | 21:70 | `04:53` |

`21b:63`’s `02:56:00` passes because `1788947760` is on that line. Both executable window guards pass because their epochs are on their lines.

**Additional semantic misses:** the regex accepts eight-hex activation IDs, although `git rev-parse --verify <id>^{commit}` rejects them. Thus these lines also lack an actual qualifying same-line source despite passing R3:

- `21b:305` — `01:33:28`, masked by activation `1ef89702`.
- `21b:310` — `01:41:58`, masked by activation `784a764e`.
- `21b:329` — `01:48` expectation anchor, masked by the addressee’s activation ID.
- `21:41` — quoted launch time `00:51`, masked by activation `1ef89702`.
- `21:43` — acknowledgement-write claim `~00:55`, masked by activation `1ef89702`.

A lexical rejection does **not** establish falsity: the copied census supports `00:46:54` and `04:53:15`; the sleep artifact supports `00:39:32`. Conversely, a regex pass does not establish provenance.

**Same-signature:** **SURVIVES hand-typed event times / unsupported self-observations**, in pre-existing narrative. **NONE SURVIVES** for hard-coded operative identity, non-fatal admission guards, pre-move real-custody writes, duplicated authoritative handback text, cure in the wrong block, or a new commit message claiming an absent operational cure. PID `48645` remains a named leaked-process rejection check; the census derives its own identity from the lock. Authoritative writer-text counts remain `1/1/1`.

**New defects introduced by f9205c49/a2be9591:** none established. D3’s historical-bound match and D6’s overlong command both predate the delta. Their literal acceptance failures remain explicit.

**Executed bench evidence**

Scratch creation failed as recorded in V3. The following are **in-memory/stdin substitutes**, not the requested mktemp evidence:

| Bench | Execution | Observed |
|---|---|---|
| B window, `1788945299` | Extracted B guard unchanged; `date()` returns fake epoch; `zsh -f -c` | `rc=0; PROCEED` |
| B window, `1788945300` | Same harness | `rc=1; ABORT: outside the arm window 01:56-02:15 PDT 2026-09-09 (t0-3600 .. t0-2460)` |
| B window, `1788944159` | Same harness | Same abort, `rc=1` |
| Missing-plan uninstall | Exact command V4 | `rc=2; plan not found: /dev/null/pr295-absent-plan.json` |
| Census with reparented daemon | Extracted PY unchanged; mocked lock `{"pid":4242}` and ps stdout | `rc=1; foreign census matches: [(9001, 'claude daemon run')]` |
| Census with own tree only | Same mocks, daemon row removed | `rc=0; foreign census matches: []` |

Fake ps input was:

```text
4242 1 claude -p magistrate
4243 4242 claude -p child
4244 4243 codex mcp-server
9001 1 claude daemon run
```

The census harness patched `os.path.expanduser`, `builtins.open` to an `io.StringIO` lock, and `subprocess.run` to the fake table. It asserted the derived PID, exact foreign list, and exit code.

Installer inspection confirms missing-plan rejection at line 29 precedes uninstall at lines 170–175; deletion must follow uninstall. No uninstall reached launchd.

`git diff --check f712d0c9..a2be9591` passed. Final HEAD and upstream remained `a2be9591954c607c3505ffa4c25559a30519d94a`; working tree remained clean. No repository files or real custody paths were written.

## Residual risk

Mandatory filesystem-backed benches remain unexecuted because the enforced read-only sandbox rejected scratch creation. No live arming or hardware validation was attempted. The lead’s next step is to rerun those benches and disposition the two literal acceptance mismatches.

VERDICT: NOT LANDABLE — ENV1 blocks completion of the required verification; D3/D6 literal acceptance also remains unresolved.