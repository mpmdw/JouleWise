SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["configs/launchd/com.joulewise.night.plist.template","scripts/install_night_agent.sh","scripts/run_night.py","tests/test_install_night_agent.py","tests/test_run_night.py","docs/process/NIGHT_HANDBACK.md","docs/phase_2/derivation_night_runbook.md"]

# Lane NIGHT-INTERPRETER-PIN-01 — pin the night driver's interpreter and preflight its imports at arm time

You are working in the linked worktree at your current directory (branch `fix/2026-09-11-night-interpreter-pin`, from main 1dddcfea). Do not touch any other checkout. Commit your work on this branch as you go (small commits, imperative subjects). Do not push. Do not edit RUN_STATE.md, TASK_QUEUE.md, or anything outside WRITE_SCOPE; if you believe another path must change, finish everything else and stop with a NEEDS_SCOPE early return naming the path and why.

## The defect (worked example — this is what happened at 02:56 PDT on 2026-09-11)

`scripts/install_night_agent.sh` renders `configs/launchd/com.joulewise.night.plist.template` into two LaunchAgents. The template's ProgramArguments begin `/usr/bin/env`, `python3`, and its EnvironmentVariables set `PATH=/Users/edr/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin`. Under that PATH, `python3` resolved to `/usr/bin/python3`, the macOS Command Line Tools interpreter, Python 3.9.6. `scripts/run_night.py` line ~1417 does a lazy `from joulewise import arm_readiness`, and `joulewise/arm_readiness.py:26` does `from datetime import UTC, datetime`, which exists only on Python 3.11+. Result: the night agent crashed with `ImportError: cannot import name 'UTC' from 'datetime'` before running any census, gate, or chain. `pyproject.toml` declares `requires-python >= 3.11`. The 2026-09-09 night ran because its head predates that import (arrived 2026-09-08). Nothing at arm time checked the interpreter the plist would use.

Two facts to keep straight: (1) the DRIVER interpreter (what runs `run_night.py` under launchd) is what failed; (2) the CHAIN interpreter is already pinned by the driver for v2 plans as `<measurement_root>/.venv/bin/python` (run_night.py ~line 434 and ~1256) and is not the problem.

## What to build

1. **Template.** Replace the two entries `/usr/bin/env` + `python3` with a single `@@PYTHON@@` placeholder rendered to an ABSOLUTE interpreter path. No `env`, no PATH lookup for the interpreter. Keep everything else byte-identical.

2. **Installer `--python ABS_PATH` (install and `--render-only` only).** Resolution order: an explicit `--python` wins; otherwise, for a v2 plan, default to `<measurement_root>/.venv/bin/python` if that file exists and is executable; otherwise refuse with exit 2 and a one-line message that names the missing path and says to pass `--python`. Refuse (exit 2, naming the value) a relative path, a path that is not an executable regular file, or an interpreter whose `sys.version_info[:2]` is below the minimum. Define the minimum ONCE in `scripts/run_night.py` as `MIN_PYTHON = (3, 11)` with a comment pointing at `pyproject.toml` `requires-python`; the installer must read it from there (via the pinned interpreter) rather than hard-code a second copy. Every python invocation the installer makes for the INSTALL path (plan parsing, DEADMAN_HOUR lookup, plist rendering) must run under the validated `--python` interpreter, not `/usr/bin/python3` — importing `scripts.run_night` under a 3.9 interpreter is the same class of fragility. The UNINSTALL path must keep working with no `--python` and no venv (it may keep `/usr/bin/python3` for the plain JSON read of `custody_root`, or use zsh; it must not import project modules).

3. **Driver `preflight` subcommand.** Add `run_night.py preflight --plan PLAN.json`, which: asserts `sys.version_info[:2] >= MIN_PYTHON`; imports, eagerly, every project module that the `run`, `dead-man` and `rehearse` paths import lazily inside functions (grep `run_night.py` for in-function `import`/`from ... import` and list them; the cleanest cure is to hoist those lazy imports to module scope so that "the module imported" IS the preflight — do that unless a lazy import exists for a documented reason, in which case import it in `preflight` explicitly and say why in a comment); parses the plan through the same `NightPlan` path the installer uses; prints one JSON line `{"preflight": "ok", "python": sys.executable, "version": "3.14.7", "modules": [...]}` and exits 0. Any failure exits non-zero with the exception on stderr (no traceback swallowing). The preflight must NOT touch the custody root, the census, launchctl, or the network.

4. **Installer runs the preflight before rendering.** Under the same environment the plist will have — build it explicitly with `env -i PATH="$courier_path" HOME="$HOME"` (use the exact PATH value the template receives) — run `"$python" -B "$repo/scripts/run_night.py" preflight --plan "$plan"`. Non-zero → refuse install with exit 2, echoing the preflight's stderr. `--render-only` also runs it. Record the preflight's JSON line on stdout so the arm record captures it.

5. **Tests (defect-shaped; each must fail on main and pass with the fix).** In `tests/test_install_night_agent.py`, following the existing fake-launchctl harness: (a) the rendered plists' ProgramArguments[0] is the absolute interpreter and no element equals `/usr/bin/env` or `python3`; (b) `--python` pointing at a fake interpreter script whose `sys.version_info` reports (3, 9) is refused with exit 2 and the message names 3.9 and the minimum — build the fake so the version check sees 3.9 (e.g. a wrapper that runs the real python with a `sitecustomize` or an argument-inspecting script; keep it simple and explain the trick in a comment); (c) install is refused when the preflight exits non-zero (e.g. a fake driver checkout whose `joulewise/arm_readiness.py` raises ImportError on import); (d) default derivation from `<measurement_root>/.venv/bin/python` when present and no `--python` given; refusal naming that path when absent; (e) `--uninstall` still works with no `--python`, no venv, and both pin mismatches (extend the existing test). In `tests/test_run_night.py`: (f) `preflight` exits 0 and prints the JSON line under the real interpreter; (g) `preflight` exits non-zero when a lazily-required module cannot be imported (monkeypatch `sys.modules` or `builtins.__import__` for the named module); (h) `MIN_PYTHON` equals the `requires-python` floor parsed from `pyproject.toml`.

6. **Docs (the two files in scope only).** In `docs/process/NIGHT_HANDBACK.md` and `docs/phase_2/derivation_night_runbook.md`: every quoted `install_night_agent.sh` install command gains the interpreter (either the venv default, stated, or an explicit `--python`); any sentence claiming a stub checkout needs no venv or that `python3` on PATH suffices is corrected; add a SHORT paragraph explaining the mechanism to a reader who has never seen it, using the 2026-09-11 02:56 crash as the concrete example, every term of art glossed at first use (a "LaunchAgent" is a macOS launchd job file; a "preflight" here is running the driver's imports under the exact interpreter the job file names, before the job is installed). Do not touch other doc sections.

## Verification you must run and report

- `python3 -m unittest tests.test_install_night_agent tests.test_run_night -v` (rc and counts).
- `python3 -m compileall -q scripts joulewise` rc 0.
- `scripts/install_night_agent.sh --render-only /tmp/interp-pin-render --plan <a v2 plan fixture you author in a temp dir> --hour 2 --minute 56 --python "$(command -v python3)"` — paste the rendered ProgramArguments and the preflight JSON line.
- Show, by running it, that the OLD template under `env -i PATH=/usr/bin:/bin` resolves `python3` to a 3.9 interpreter on this host (`env -i PATH=/usr/bin:/bin /usr/bin/env python3 --version`) — this is the counterfactual the tests encode.
- The canonical suite is NOT yours to run; the lead runs the sharded replay.

## Rules

- Do not run anything that arms a night, touches `~/night-custody`, `~/Library/LaunchAgents`, or `launchctl` outside the test harness's fake.
- Do not start or continue any `[QUIET-MAC]` measurement.
- If any contract in `docs/contracts/` pins the plist's ProgramArguments shape or the installer's flags, do not silently change the contract: finish the code and stop with NEEDS_RULING quoting the clause.
- Final message: the claude-codex-report/v1 envelope (the --genre implementation contract) with changed files, commits, test output, and any early-return.
