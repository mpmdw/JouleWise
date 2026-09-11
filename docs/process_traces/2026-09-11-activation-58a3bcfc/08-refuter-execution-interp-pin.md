```json
{
"schema":"claude-codex-report/v1","genre":"review","status":"blocked","completion":"partial",
"summary":"Read-only probes found a future parser diagnostic weakness; sandbox blocks the required installer, temporary-fixture, and baseline-checkout verification.",
"workspace":{"base_requested":"1dddcfea","base_mode":"exact","head_start":"17c26a1a3df77847cb109f983014f723b44458ca","head_end":"17c26a1a3df77847cb109f983014f723b44458ca","upstream_end":"1dddcfea573d85ee8facebc2b50dac412cb3b69f","branch":"fix/2026-09-11-night-interpreter-pin"},
"pathspec":[],"unowned_dirty":[],
"verdict":{"decision":"BLOCKED","findings":[{"id":"F1","severity":"nit","file":"scripts/install_night_agent.sh:71","title":"Parsing the whole driver under the rejected interpreter makes the version diagnostic depend on old syntax compatibility."}]},
"verification":[
{"id":"V1","kind":"other","cmd":"/opt/homebrew/bin/python3 -B -c 'import tempfile; print(tempfile.mkdtemp(prefix=\"night-pin-execution-\", dir=\"/tmp\"))'","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["PermissionError: [Errno 1] Operation not permitted: '/tmp/night-pin-execution-3ln9wi4b'"]},"expected":{"exit_code":0,"tail_regex":"/tmp/night-pin-execution-"}},
{"id":"V2","kind":"smoke","cmd":"/bin/zsh scripts/install_night_agent.sh --render-only /tmp/night-pin-render-denied --plan tests/fixtures/night_plan_v1_retired.json --hour 2 --minute 56 --python /usr/bin/python3","cwd":".","observed":{"result":"fail","exit_code":2,"tail":["scripts/install_night_agent.sh:66: can't create temp file for here document: operation not permitted"]},"expected":{"exit_code":2,"tail_regex":"interpreter /usr/bin/python3 reports Python 3.9; minimum is 3.11"}},
{"id":"V3","kind":"smoke","cmd":"/opt/homebrew/bin/python3 -B -c 'import pathlib, subprocess\nroot=pathlib.Path.cwd()\ninstaller=(root/\"scripts/install_night_agent.sh\").read_text()\nprobe=installer.split(\"<<'\\''PYTHON_CHECK'\\'' || exit 2\\n\",1)[1].split(\"\\nPYTHON_CHECK\",1)[0]\nfor python in [\"/usr/bin/python3\",\"/opt/homebrew/bin/python3\"]:\n    argv=[python,\"-B\",\"-\",str(root/\"scripts/run_night.py\"),python]\n    p=subprocess.run(argv,input=probe,text=True,capture_output=True)\n    print(\"ARGV=\"+repr(argv)+\" RC=\"+str(p.returncode))\n    print(p.stdout+p.stderr,end=\"\")\nfuture = \"\"\"\nimport builtins, io\noriginal_open=builtins.open\ndef future_open(path,*a,**kw):\n    with original_open(path,*a,**kw) as stream: text=stream.read()\n    return io.StringIO(text+\"\\\\nmatch 1:\\\\n    case 1: pass\\\\n\")\nbuiltins.open=future_open\n\"\"\"\np=subprocess.run([\"/usr/bin/python3\",\"-B\",\"-\",str(root/\"scripts/run_night.py\"),\"/usr/bin/python3\"],input=future+probe,text=True,capture_output=True)\nprint(\"FUTURE_MATCH_SYNTAX RC=\"+str(p.returncode))\nprint(p.stdout+p.stderr,end=\"\")\n'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["interpreter /usr/bin/python3 reports Python 3.9; minimum is 3.11","FUTURE_MATCH_SYNTAX RC=1","SyntaxError: invalid syntax"]},"expected":{"exit_code":0,"tail_regex":"SyntaxError: invalid syntax"}},
{"id":"V4","kind":"smoke","cmd":"/usr/bin/env -i PATH=/usr/bin:/bin HOME=/tmp/x /opt/homebrew/bin/python3 -B /Users/edr/code/JouleWise-wt-interp-pin/scripts/run_night.py preflight --plan /dev/stdin","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["{\"preflight\": \"ok\", \"python\": \"/opt/homebrew/opt/python@3.14/bin/python3.14\", \"version\": \"3.14.7\", \"modules\": [\"joulewise.arm_readiness\", \"joulewise.arm_readiness_evidence_t0\", \"joulewise.t0_rehearsal\", \"joulewise.night_gate\", \"joulewise.measurement_liveness\"]}"]},"expected":{"exit_code":0,"tail_regex":"\"preflight\": \"ok\""}},
{"id":"V5","kind":"smoke","cmd":"/opt/homebrew/bin/python3 -B -c 'import json, pathlib, plistlib, subprocess, sys\nfrom unittest.mock import patch\nroot=pathlib.Path.cwd()\ntext=(root/\"scripts/install_night_agent.sh\").read_text()\nrender=text.split(\"<<'\\''PY'\\''\\n\")[-1].split(\"\\nPY\\n\",1)[0]\nfor python in [\"/opt/homebrew/bin/python3\", \"/tmp/python space \\\"double\\\" '\\''single'\\'' & pinned\"]:\n    for label,mode in [(\"com.joulewise.night\",\"run\"),(\"com.joulewise.night.deadman\",\"dead-man\")]:\n        captured=[]\n        sys.argv=[\"-\",str(root/\"configs/launchd/com.joulewise.night.plist.template\"),\n            \"/tmp/unused-output\",label,mode,str(root),\"/tmp/execution-plan.json\",\n            \"/tmp/execution-custody\",\"2\" if mode==\"run\" else \"7\",\"56\" if mode==\"run\" else \"0\",\n            \"/tmp/claude\",\"/tmp:/usr/bin:/bin:/usr/sbin:/sbin\",\"launchd.\"+mode,python]\n        with patch.object(pathlib.Path,\"write_text\",lambda self,s,**kw: captured.append(s)):\n            exec(compile(render,\"installer-render-snippet\",\"exec\"),{})\n        rendered=captured[0]\n        lint=subprocess.run([\"/usr/bin/plutil\",\"-lint\",\"-\"],input=rendered,text=True,capture_output=True)\n        argv=plistlib.loads(rendered.encode())[\"ProgramArguments\"]\n        print(label+\" ProgramArguments=\"+json.dumps(argv))\n        print(\"LINT_RC=\"+str(lint.returncode)+\" \"+lint.stdout.strip()+\" \"+lint.stderr.strip())\n        print(\"ARGV0_EXACT=\"+str(argv[0]==python))\n'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["LINT_RC=0 <stdin>: OK ","ARGV0_EXACT=True"]},"expected":{"exit_code":0,"tail_regex":"ARGV0_EXACT=True"}},
{"id":"V6","kind":"smoke","cmd":"/usr/bin/env -i PATH=/usr/bin:/bin HOME=/tmp/x /usr/bin/python3 -B scripts/magistrate_watchdog.py --help","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["RuntimeError: Python 3.9 is below the minimum 3.11"]},"expected":{"exit_code":1,"tail_regex":"RuntimeError: Python 3.9 is below the minimum 3.11"}},
{"id":"V7","kind":"test","cmd":"/opt/homebrew/bin/python3 -B -c 'import pathlib, subprocess, types\nfrom tests.test_run_night import NightDriverTests\np=pathlib.Path(\"scripts/run_night.py\").resolve()\nfor label,source in [(\"HEAD\",p.read_text()),(\"origin/main\",subprocess.check_output([\"git\",\"show\",\"origin/main:scripts/run_night.py\"],text=True))]:\n    driver=types.ModuleType(\"review_driver\")\n    driver.__file__=str(p)\n    exec(compile(source,str(p),\"exec\"),driver.__dict__)\n    case=NightDriverTests(\"test_minimum_python_matches_project_requires_python\")\n    case.driver=driver\n    try:\n        case.test_minimum_python_matches_project_requires_python()\n    except Exception as exc:\n        print(label+\": \"+type(exc).__name__+\": \"+str(exc))\n    else:\n        print(label+\": PASS\")\n'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["HEAD: PASS","origin/main: AttributeError: module 'review_driver' has no attribute 'MIN_PYTHON'"]},"expected":{"exit_code":0,"tail_regex":"origin/main: AttributeError:"}}
],
"flags":[
{"id":"G1","kind":"environment","level":"blocking","text":"Read-only sandbox denies /tmp writes and zsh here-document temporary files. Full installer probes, executable-path fixtures, isolated uninstall, and three tests against a /tmp origin/main checkout remain unexecuted.","needs":"Lead reruns these checks in a session permitting temporary files under /tmp; no repository write expansion is needed."},
{"id":"G2","kind":"verification_gap","level":"nonblocking","text":"Renderer ran with its output captured in memory. Preflight used an authored v2 plan on stdin. V7 ran one unchanged test body without its disk-writing setUp; it is not a baseline suite or checkout replay.","needs":""}
]
}
```

## Findings

**F1 — NIT: future supported syntax defeats the old-interpreter diagnostic.** At [scripts/install_night_agent.sh:71](/Users/edr/code/JouleWise-wt-interp-pin/scripts/install_night_agent.sh:71), the candidate interpreter parses the entire driver before reading `MIN_PYTHON`.

The exact V3 command above executed the installer’s extracted probe:

- Real `/usr/bin/python3`: **rc 2**, `interpreter /usr/bin/python3 reports Python 3.9; minimum is 3.11`.
- `/opt/homebrew/bin/python3`: **rc 0**.
- Real 3.9 with `match 1: case 1: pass` appended **in memory**: **rc 1**, traceback ending `SyntaxError: invalid syntax`.

Thus today’s file parses under 3.9. Future valid 3.10+ syntax can replace the useful candidate/version/minimum message with a parser traceback. The installer would still refuse with rc 2 through `|| exit 2`, but the explanation becomes misleading. Extract and parse only the minimum assignment to avoid that dependency.

The simulated-3.9 test at [tests/test_install_night_agent.py:185](/Users/edr/code/JouleWise-wt-interp-pin/tests/test_install_night_agent.py:185) uses the modern interpreter’s parser, so it cannot detect this failure mode. This is future robustness, not a demonstrated failure of today’s supported installation.

## Residual risk

**Required execution coverage remains incomplete.** `/tmp` directory creation was denied, and the actual installer stopped at its here-document before executing Python. No bypass was attempted. The full diff was read; repository status remained clean at `17c26a1a`.

1. **Real 3.9 installer:** the full authored-v2-fixture test was blocked. V2 used an existing fixture solely to reach the earlier version check; zsh failed at line 66. V3 independently established that the unchanged Python probe produces the intended refusal today.

2. **Homebrew interpreter:** the real driver preflight passed using an authored v2 JSON plan supplied through stdin. Its exact success JSON is in V4. The complete installer path remains unverified.

   V5 executed the unchanged renderer with output captured in memory. Its rendered `ProgramArguments` were:

   ```text
   com.joulewise.night:
   ["/opt/homebrew/bin/python3", "/Users/edr/code/JouleWise-wt-interp-pin/scripts/run_night.py", "run", "--plan", "/tmp/execution-plan.json", "--courier-bin", "/tmp/claude"]

   com.joulewise.night.deadman:
   ["/opt/homebrew/bin/python3", "/Users/edr/code/JouleWise-wt-interp-pin/scripts/run_night.py", "dead-man", "--plan", "/tmp/execution-plan.json", "--courier-bin", "/tmp/claude"]
   ```

   These are isolated renderer results, not installed files. The stdin preflight fixture followed the test’s v2 shape: `REHEARSAL_STUB`, both heads `17c26a1a…`, measurement root this checkout, `/bin/true` chain, `/tmp` custody/registration paths, and `authored_epoch_s=time.time()`.

3. **Spaces, quotes, ampersand:** V5 also rendered `/tmp/python space "double" 'single' & pinned`. Both plists passed `/usr/bin/plutil -lint -` with `<stdin>: OK`; `plistlib` recovered that entire string as exactly `ProgramArguments[0]`. Creating and executing the corresponding interpreter fixture was blocked. XML escaping is at [installer:188](/Users/edr/code/JouleWise-wt-interp-pin/scripts/install_night_agent.sh:188).

4. **Default venv derivation:** fixture execution was blocked. Inspection of [installer:47](/Users/edr/code/JouleWise-wt-interp-pin/scripts/install_night_agent.sh:47) shows that `-f`/`-x` follow symlinks and the lexical absolute `.venv/bin/python` path is preserved. On this host, the same file check accepted `/opt/homebrew/bin/python3`, whose link target is `../Cellar/python@3.14/3.14.7/bin/python3`. Shell wrappers also satisfy these file checks; their subsequent version/preflight behavior depends on what they execute. Neither wrapper nor derived-venv scenarios received the requested execution proof.

5. **Uninstall without project modules:** source inspection supports the intended isolation: [installer:144](/Users/edr/code/JouleWise-wt-interp-pin/scripts/install_night_agent.sh:144) uses `/usr/bin/python3` for plain JSON; the driver import is inside `! uninstall`. The isolated uninstall fixture and fake-launchctl execution were blocked.

6. **Hoisted imports:** no import cycle appeared in the fresh-interpreter preflight. Module-level AST inspection found constants, constructors, regex compilation, and the signature assertion at [arm_readiness_evidence_t0.py:2431](/Users/edr/code/JouleWise-wt-interp-pin/joulewise/arm_readiness_evidence_t0.py:2431); that assertion only inspects the author function’s parameters. A separate audit-hook execution covering import and preflight reported `AUDIT_SIDE_EFFECTS=[]` for file mutations, subprocess/process launches, and socket operations. No dead-man operational action was invoked.

7. **Minimal-environment preflight:** V4 passed with `env -i PATH=/usr/bin:/bin HOME=/tmp/x` and `-B`, matching the installer’s bytecode setting. No mutation was observed by the audit hook. This is Python-level observation after interpreter startup, not native syscall tracing or verification of arbitrary interpreter startup customization.

8. **Other entry points:** the guard **does break the watchdog under 3.9**: V6 fails at [magistrate_watchdog.py:44](/Users/edr/code/JouleWise-wt-interp-pin/scripts/magistrate_watchdog.py:44). Loading the `origin/main` driver bytes in memory allowed the unchanged watchdog’s `--help` to complete under 3.9. However, the watchdog installer already rejects `/usr/bin/python3` and pins its selected executable at [install_magistrate_watchdog.sh:56](/Users/edr/code/JouleWise-wt-interp-pin/scripts/install_magistrate_watchdog.sh:56), and the project requires 3.11+. I therefore have no demonstrated supported-deployment regression. Installed LaunchAgents were not inspected.

   Repository grep also located driver imports/loaders in `tests/test_night_gate.py:1036`, `tests/test_gen_derivation_night.py:1079`, and the night-driver/watchdog test harnesses. Those likewise require a supported interpreter after this change.

9. **Candidate AST compatibility:** executed; see F1.

10. **New-test baseline audit:** the requested three tests against a `/tmp` checkout were **not run**. The following classifications are source-derived except the minimum-version test body, which V7 executed against both driver versions:

| Test | Expected on `origin/main` | Reason |
|---|---|---|
| `test_explicit_python_is_the_only_interpreter_in_both_agents` | FAIL | Unknown `--python`; success assertion fails. |
| `test_explicit_python_overrides_venv_and_preserves_xml_characters` | FAIL | Unknown `--python`. |
| `test_python_39_is_refused_with_version_and_minimum` | FAIL | Usage output lacks candidate/version/minimum diagnostic. |
| `test_python_must_be_an_absolute_executable_regular_file` | FAIL | Usage output lacks `invalid --python`. |
| `test_default_python_is_measurement_venv` | FAIL | Old installer emits no preflight JSON and retains `env python3`. |
| `test_missing_default_python_names_path_and_explicit_option` | FAIL | Old installer does not require or diagnose the missing venv. |
| `test_failed_import_preflight_refuses_install_and_render` | FAIL | Unknown `--python`; expected import-failure witness is absent. |
| `test_preflight_emits_json_without_running_or_creating_custody` | FAIL | `preflight` is not a recognized command. |
| `test_preflight_refuses_every_formerly_lazy_project_import` | FAIL | Parser refusal lacks the required dependency ImportError. |
| `test_minimum_python_matches_project_requires_python` | FAIL — body executed | `AttributeError: … has no attribute 'MIN_PYTHON'`. |

The **extended existing** `test_uninstall_ignores_both_pin_mismatches_and_invokes_launchctl` should also fail on main: its new driver-less checkout makes main’s unconditional driver import fail. No newly added test appears to pass on main, but the required baseline execution proof remains outstanding.

Next exact step: rerun items 1–5 and at least three new tests against `origin/main` in a session permitting `/tmp` fixtures.

**VERDICT: BLOCKED** — required verification is incomplete; no current supported-runtime blocker was demonstrated.