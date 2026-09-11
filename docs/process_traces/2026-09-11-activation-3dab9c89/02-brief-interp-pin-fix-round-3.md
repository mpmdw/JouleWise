SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["scripts/install_night_agent.sh", "tests/test_install_night_agent.py"]

FIX ROUND 3 for lane NIGHT-INTERPRETER-PIN-01 (PR #321), branch fix/2026-09-11-night-interpreter-pin at HEAD 1b893ec4; this cwd is the worktree. Do not commit (the sandbox cannot; the lead commits). Temp files only under /tmp.

DEFECT (CI-only; found by GitHub Actions run 34611633826 on ubuntu, jobs "pr-fast (1)" and "test (3.14, 4)"; the macOS module run passes 106/106, which is why seat 04 and refuters 08/09 missed it):
scripts/install_night_agent.sh:52 derives the default interpreter with
    measurement_root="$(/usr/bin/plutil -extract measurement_root raw -o - "$plan")"
plutil is macOS-only. On the Linux runner every install-path test that omits --python fails. Exact CI assertion lines:
    AssertionError: 0 != 2 : .../scripts/install_night_agent.sh:52: no such file or directory: /usr/bin/plutil
    AssertionError: 'refusing --hour 7: it is the dead-man hour (DEADMAN_HOUR=7)' not found in '.../install_night_agent.sh:52: no such file or directory: /usr/bin/plutil\ncannot derive measurement_root/.venv/bin/python from /tmp/.../dead-man-hour/install-plan.json; pass --python ABS_PATH\n'
    AssertionError: 'courier unavailable' not found in '... no such file or directory: /usr/bin/plutil ...'
    AssertionError: 2 != 0 : .../install_night_agent.sh:52: no such file or directory: /usr/bin/plutil
CI (ubuntu, Python 3.11 and 3.14) is the project's Linux oracle; main was green before this branch.

REQUIRED CURE (lead decision; not open for redesign):
1. Remove the plutil dependency from the bootstrap read. Read measurement_root from the plan JSON with a stdlib-only parse under whatever python3 the ambient PATH offers, e.g.
    measurement_root="$(/usr/bin/env python3 -B -S -c 'import json, sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["measurement_root"])' "$plan" 2>/dev/null)" || { <existing message>; exit 2; }
   State in a code comment WHY this is safe under any Python 3, including the 3.9 that caused the 2026-09-11 defect: it imports only the json module, never the project or the driver; the interpreter the plists will name is still the derived venv python and is still validated by the MIN_PYTHON check that follows. Keep the existing refusal text "cannot derive measurement_root/.venv/bin/python from $plan; pass --python ABS_PATH" and rc 2 for: no python3 on PATH, unreadable JSON, or a missing measurement_root key. An empty string result must also refuse.
2. Add no new flag. Do not touch --python, the MIN_PYTHON version check, the preflight, the template, uninstall, or any doc.
3. Tests (tests/test_install_night_agent.py): keep every existing test. Add two defect-shaped regressions: (a) a text tripwire asserting the installer contains no "plutil" token, with a one-line comment naming CI run 34611633826 and why (Linux runner); (b) the default derivation succeeds with --render-only under a PATH that offers python3 only through a temp directory symlink to sys.executable (env -i PATH="<tmp_bin>:/bin:/usr/bin" HOME=...), proving the read needs nothing but a python3 on PATH; paste ProgramArguments[0] equality with <measurement_root>/.venv/bin/python. If the module already has a helper that creates a fake .venv/bin/python in the temp measurement_root, reuse it. Both new tests must fail against 1b893ec4 by inspection (say how) and pass after the cure.

VERIFICATION (paste exact tails into the envelope):
    V1  python3 -m unittest tests.test_install_night_agent tests.test_run_night      (rc 0; counts)
    V2  /bin/zsh -n scripts/install_night_agent.sh
    V3  python3 -m compileall -q scripts joulewise
    V4  the render-only default-derivation run of test (b) executed by hand under the restricted PATH; paste stdout/stderr and rc
    V5  grep -c plutil scripts/install_night_agent.sh   (expected 0, grep rc 1)

STOP RULES: if the cure needs any path outside WRITE_SCOPE, finish the authorized work and return partial with a blocking scope_expansion flag. If a test in the module already asserts the plutil read or a plutil-shaped stderr, list it under findings rather than deleting it silently, then adapt it and say so. Never run install for real (only --render-only and the fake launchctl seams the tests already use).
