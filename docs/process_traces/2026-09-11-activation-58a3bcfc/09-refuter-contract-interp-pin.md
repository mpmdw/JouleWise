# Refuter — CONTRACT lens — lane NIGHT-INTERPRETER-PIN-01

- Worktree: `/Users/edr/code/JouleWise-wt-interp-pin`, branch `fix/2026-09-11-night-interpreter-pin`, HEAD `17c26a1a`, base `origin/main` `1dddcfea`.
- Read: brief `03-brief-NIGHT-INTERPRETER-PIN-01.md`, seat report `04-seat-interp-pin-report.md`, full `git diff origin/main..HEAD` (7 files, +331/−36).
- Executed this session (read-only, temp only): `python3 -m unittest tests.test_install_night_agent tests.test_run_night` → `Ran 105 tests in 13.701s / OK`, rc 0. Real-3.9 probe (below). No git mutation, no `~/night-custody`, no `~/Library/LaunchAgents`, no `launchctl`, no network.

---

## 1. Contract-document sweep

### 1.1 Nothing in `docs/contracts/*.md` pins the plist argv or the installer's flags — no NEEDS_RULING was owed

Bench-verified: `grep -rn "usr/bin/env" docs/contracts/ docs/process/ docs/phase_2/` returns nothing, and `grep -rln "ProgramArguments" docs/contracts/ docs/process/ docs/phase_2/` returns nothing. The brief's clause "If any contract in `docs/contracts/` pins the plist's ProgramArguments shape or the installer's flags … stop with NEEDS_RULING" therefore did not fire. The seat was right not to raise one. **No finding.**

Supporting precedent, not a conflict: `docs/process/MAGISTRATE_WATCHDOG.md:175` already promises the sibling installer *"pins the installing `python3` process's absolute `sys.executable`"*. The night installer was the outlier; this diff makes the two consistent.

### 1.2 BLOCKER (for arming, not for merging) — the arm runbook of record now exits 2

`docs/process_traces/2026-09-09-rehearsal-harvest/67-arm-runbook-rehearsal-20260911.md:173`

```
scripts/install_night_agent.sh --plan "$SCRATCH/night_plan.json" --hour 2 --minute 56 --render-only "$SCRATCH/render"
```

and `:252`

```
if ! scripts/install_night_agent.sh --plan "$NIGHT_CUSTODY/night_plan.json" --hour 2 --minute 56; then
```

Neither carries `--python`. For a REHEARSAL_STUB the plan's `measurement_root` is the `/private/tmp/joulewise-rehearsal-…-checkout` detached checkout, which has no `.venv`. Post-merge both commands take `scripts/install_night_agent.sh:55-58` and die:

```
missing executable interpreter: <measurement_root>/.venv/bin/python; pass --python ABS_PATH
```

This is fail-closed and loud (rc 2, no custody created, nothing armed), so it cannot arm a broken night — but it *will* stall an unattended arming window, and runbook 67 is the document the headless magistrate executes. `docs/decision_log.md:11436` (D-175 condition 2, *"validate with `install_night_agent.sh --render-only` from the pinned measurement checkout"*) has the same gap: every D-175 stub arm now requires either a venv inside the `/private/tmp` stub root or an explicit `--python`, and D-175 says neither. Outside the seat's WRITE_SCOPE, so not a seat defect — but it must land, or be explicitly deferred with a named owner, **before the next arm**. Lowest-cost cure: append `--python "$PY"` (or a `PY=` export) to runbook 67 `:173` and `:252`, and a dated D-175 addendum.

`docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md:496,651` (the real G2-a night) also omits `--python`, but its measurement clone does have `.venv`, so the default derivation carries it. **SHOULD_FIX**: state there that the clone's venv is now load-bearing at *install* time, not only at chain time.

### 1.3 SHOULD_FIX — `docs/process/NIGHT_HANDBACK.md` now contradicts itself inside one file

The diff added, at `:163-165`, *"At 02:56 PDT on 2026-09-11, the night driver crashed before any gate"*. Three sections the brief forbade touching still describe that night as pending or successful:

- `:44-45` — *"Plan `rehearsal-20260911`, class `REHEARSAL_STUB`, **is planned for** 2026-09-11 at 02:56:00 PDT"*
- `:104-105` — *"`result.json` (**expected verdict `REHEARSAL_ONLY`**, `chain_exit_code` 0)"*
- `:115-122` — §Next lane: *"The relaunched magistrate … **harvests** `result.json`, the receipt or refusal, the courier message id"* / *"Acceptance requires `receipt.json` verdict `REHEARSAL_ONLY`"*
- `:57-59` — *"item 6 is re-satisfied only if its receipt is not refused"* — there is no receipt at all.

Not a seat defect (brief: *"Do not touch other doc sections"*), but the file is the headless magistrate's instruction source and currently says both that the night crashed and that its results are waiting to be harvested. Reconcile in the same PR or in the immediately following bookkeeping commit.

### 1.4 SHOULD_FIX — stale `file:line` pins the diff invalidated

- `docs/contracts/pack_night_go_receipt.md:637` pins *"`scripts/install_night_agent.sh:39–75,132–141` validated absolute plan-path installation"*. Post-diff, the `NightPlan` validation block is `:82-118` and the plan-path rendering is `:180-203`; `:132-141` is now the measurement-head check and courier resolution. Both ranges are stale.
- `docs/process_traces/2026-09-09-rehearsal-harvest/67-arm-runbook-rehearsal-20260911.md:192` (`install_night_agent.sh:123–125`), `:197` (`:81–96`), `:441` (`:5, 43–103, 181–216`) — all shifted by the ~+40-line insertion.

NIT-grade individually; grouped as SHOULD_FIX because the D-175/arm-runbook pins are the ones an auditor follows at arm time.

### 1.5 No "stub needs no venv" sentence survives anywhere

`grep -rni "venv" docs/process/ docs/phase_2/ docs/contracts/` (traces excluded) returns no sentence claiming a stub checkout needs no venv or that `python3` on PATH suffices. The only such promise was `NIGHT_HANDBACK.md`'s uninstall note, and the diff corrected it in place (`:156-157`). **No stale text of that class outside scope.**

---

## 2. Brief requirements 1–6

### Req 1 — template: **PASS**
`configs/launchd/com.joulewise.night.plist.template:9` is now the single `<string>@@PYTHON@@</string>`; `/usr/bin/env` and `python3` are gone. The diff touches only those three lines; the rest of the file is byte-identical (`git diff` shows `3 +-`, one hunk).

### Req 2 — installer `--python`: **PASS**, with one message-quality finding

| Clause | Evidence | Verdict |
|---|---|---|
| Explicit `--python` wins | `install_night_agent.sh:22` sets `python_given=1`; `:48` guards the default branch on `(( ! python_given ))` | PASS |
| Default `<measurement_root>/.venv/bin/python` when present+executable | `:50-58`, derived by `/usr/bin/plutil -extract measurement_root raw -o -` — no Python, no project import, so a broken interpreter cannot poison the bootstrap | PASS |
| Refuse exit 2 naming the missing path + "pass `--python`" | `:56` `"missing executable interpreter: $python; pass --python ABS_PATH"` | PASS |
| Refuse relative / non-executable / non-regular | `:60-63` `[[ "$python" == /* && -f "$python" && -x "$python" ]]`, message `"invalid --python: $python (expected an absolute executable regular file)"` | PASS |
| Refuse interpreter below minimum | `:66-81` AST probe; bench-verified against the *real* 3.9: running that heredoc with `/usr/bin/python3` (Python 3.9.6) printed `interpreter /usr/bin/python3 reports Python 3.9; minimum is 3.11`, rc 2. I also confirmed `ast.parse` of `scripts/run_night.py` succeeds under 3.9.6, so the probe reaches its friendly message rather than a SyntaxError | PASS |
| `MIN_PYTHON` defined ONCE, comment pointing at `pyproject.toml` | `scripts/run_night.py:24` `# Keep aligned with pyproject.toml requires-python. The installer reads this literal.`, `:25` `MIN_PYTHON = (3, 11)` | PASS |
| Installer reads it rather than hard-coding a copy | `install_night_agent.sh:66-81` reads the literal by AST instead of importing the driver — **stronger than the brief asked**, and the right call: importing `scripts.run_night` under a 3.9 interpreter is the failure being cured | PASS |
| Every INSTALL-path Python invocation under the validated interpreter | `:82` plan parse, `:152` `DEADMAN_HOUR` lookup, `:180` render — all `"$python" -B` | PASS |
| UNINSTALL works with no `--python` and no venv, no project import | `:144` `/usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["custody_root"])'` — plain JSON read, no `sys.path` insert, no `joulewise`. `:146` gates the whole preflight/DEADMAN block on `(( ! uninstall ))`, so uninstall never touches `$python`. Regression at `tests/test_install_night_agent.py:380-401` deletes the courier, asserts `.venv` absent, and runs the installer from a fixture directory containing **only** `install_night_agent.sh` + the template (no `run_night.py`, no `joulewise/`) — defect-shaped, since on `origin/main` the `DEADMAN_HOUR` import ran unconditionally and would abort under `set -e` | PASS |

**SHOULD_FIX — `install_night_agent.sh:5` + `:29`, usage text advertises a combination it refuses.**
`:29` `(( uninstall && python_given )) && usage` makes `--uninstall --python` a hard usage error, but `:5` prints

```
usage: $0 --plan PLAN.json --hour H --minute M [--python ABS_PATH] [--uninstall] [--render-only DIR] [--launchctl-bin PATH]
```

— two independent optional brackets, no mutual-exclusion marker, and no message explaining *why* the invocation failed. Against the brief this is consistent in spirit (`--python` is scoped to "install and `--render-only` only"), but the brief specified scoping, not refusal, and refusal is the operator-hostile reading: an operator whose recovery block reuses one `INSTALL_ARGS` variable gets a bare usage dump. Cure: either print a specific line (`--python is not valid with --uninstall`) or spell the exclusivity in the usage string (`[--python ABS_PATH | --uninstall]`). Note the repo's own recovery sequences already pass no `--python` on uninstall (`derivation_night_runbook.md:1351-1352`, `NIGHT_HANDBACK.md:130`), so nothing in-tree breaks.

### Req 3 — `preflight` subcommand: **PASS**, with a scope caveat

- Version assertion: hoisted to module scope, `scripts/run_night.py:25-29`, so it guards *every* subcommand, not just `preflight`. Exceeds the brief.
- Lazy-import hoist: `:40-43` now imports `arm_readiness as readiness`, `arm_readiness_evidence_t0 as t0_author`, `night_gate, t0_rehearsal` eagerly, with the rationale in the comment at `:38-39` (*"so importing this driver during preflight catches failures before installation"*). Bench-verified exhaustive: `grep -n "^\s\+\(import\|from\) " scripts/run_night.py` returns **zero** lines — no in-function import survives anywhere in the driver. That is the cleanest form the brief offered.
- Plan parsed through the same path: `:1867` `_load_plan(args.plan)`, and `_load_plan` at `:920-921` is exactly `NightPlan.from_mapping(json.loads(path.read_text(encoding="utf-8")))` — the same `NightPlan.from_mapping` the installer's heredoc calls at `install_night_agent.sh:94`.
- One JSON line, exit 0: `:1868-1877`, `return 0`.
- **No custody / census / launchctl / network**: verified by reading `main()` (`:1864-1878`) and `_load_plan`. The preflight branch is the **first** branch in `main()` and returns before `run_night`, `dead_man`, or `produce_g7_control` can be reached; `_load_plan` performs one `read_text` on the plan path and nothing else. Reinforced by `tests/test_run_night.py:254-275`, which asserts `self.custody.exists()` is False after the subprocess run and then re-runs `main(["preflight", …])` with `subprocess.Popen` and `Path.mkdir` both patched to raise, plus `self.probes_mock.assert_not_called()`. **PASS.**
- Failures non-zero with the exception on stderr, no swallowing: `tests/test_run_night.py:295-297` asserts both `ImportError: missing preflight dependency: …` and `Traceback` in stderr.

**SHOULD_FIX (documentation, not code) — the preflight's coverage is narrower than the docs claim.**
The hoist covers `run_night.py`'s own lazy imports. It does **not** cover project modules imported lazily one level down, e.g. `joulewise/arm_readiness.py:3833` `from joulewise import arm_readiness_evidence as evidence_author`, `:5624` `from joulewise.analysis_manifest_v3 import (…)`, `:8052-8054` `from joulewise.calibration_ledger import …` / `from scripts import reserve_calibration_window_bracket as reserve_cli`. A `datetime.UTC`-class defect inside any of those would still reach the night. `NIGHT_HANDBACK.md:166-167` — *"A **driver preflight** here runs **the driver's imports** under that exact interpreter"* — reads as complete coverage. Either bound the sentence ("the driver's own module graph; modules the driver imports only deep inside `joulewise` are not covered") or extend the preflight. The brief scoped req 3 to `run_night.py`, so the code is PASS; the sentence is what over-promises.

**NIT — the dead-man lost its import independence.** On `origin/main` the `dead-man` path imported none of `arm_readiness` / `t0_rehearsal` / `arm_readiness_evidence_t0`; they were lazy inside the run path. After the hoist, a module-level failure in any of them kills the *dead-man* too — the safety net that exists to stand a broken night down. Mitigated by the arm-time preflight exercising exactly those imports under exactly that interpreter, and the trade (one preflight-gated failure mode vs. the silent 02:56 crash) is clearly right. Recording it so it is a known, accepted property rather than an unnoticed one.

**NIT — bytecode side effect moved.** `scripts/run_night.py:1881` sets `sys.dont_write_bytecode = True` inside `if __name__ == "__main__"`, i.e. *after* the module body runs. The three newly-hoisted imports therefore write `__pycache__` into the driver checkout at night, where previously they did not. Harmless here: `.gitignore:1` is `__pycache__/`, and the chain's cleanliness assertion is `git -C <CLONE> status --porcelain` (`scripts/gen_derivation_night.py:722`) with no `--ignored`, so the tree still reads clean. Optional hardening: add `-B` to the template's `ProgramArguments`.

### Req 4 — preflight under the plist's exact PATH: **PASS**

`install_night_agent.sh:148-149`:

```
/usr/bin/env -i PATH="$courier_path" HOME="$HOME" \
  "$python" -B "$repo/scripts/run_night.py" preflight --plan "$plan"
```

`courier_path` is built once at `:140` (`courier_path="${courier_bin:h}:/usr/bin:/bin:/usr/sbin:/sbin"`) and the *same shell variable* is passed to the renderer at `:180` and mapped to `"@@PATH@@": path` at `:196`, which fills `com.joulewise.night.plist.template:22`. Same variable, no re-derivation, so the preflight PATH and the plist PATH are byte-identical by construction. Note `:140` deliberately uses the pre-`:A` dirname while `:141` resolves `courier_bin` — that asymmetry is pre-existing and is preserved on both sides equally.

Ordering is correct: `:148` preflight → `:155` dead-man-hour refusal → `:166-169` `mkdir -p "$launch_dir"` / `mkdir -p "$custody_root/night"` → `:237-238` render → `:246` `bootstrap`. A failed preflight therefore leaves no custody directory and no plist, which the tests assert (`test_install_night_agent.py:270-273`). `--render-only` runs it too (`:146` gates on `uninstall`, not on `render_only`; the test subTests both, `:263-264`). The JSON line lands on the installer's stdout for the arm record (`test_install_night_agent.py:161-163` parses `completed.stdout.splitlines()[0]`).

**NIT** — `env -i PATH=… HOME=…` is *stricter* than the real job environment: launchd additionally injects `USER`, `LOGNAME`, `SHELL`, `TMPDIR`, `__CF_USER_TEXT_ENCODING`, `XPC_SERVICE_NAME` for a `gui/<uid>` agent. The divergence is in the safe direction (a preflight pass implies a job pass; the reverse could give a false alarm on something needing `TMPDIR`). Worth one comment line so a future reader does not "fix" it by widening.

### Req 5 — tests defect-shaped: **PASS** (none would pass on `origin/main`)

| Test | `path:line` | Why it fails on `origin/main` |
|---|---|---|
| (a) absolute interpreter, no `env`/`python3` | `test_install_night_agent.py:159-170` | `--python` is an unknown flag on main → `usage()` rc 2, `assertEqual(0, …)` fails |
| explicit python beats venv, XML-safe path | `:172-182` | same unknown flag |
| (b) fake 3.9 refused, names 3.9 and the minimum | `:184-203` | rc is 2 on main too, but from `usage()`; `assertIn("minimum is 3.11", stderr)` fails |
| absolute/executable/regular refusals | `:205-215` | `assertIn(f"invalid --python: {value}")` fails |
| (d) default from `<measurement_root>/.venv/bin/python` | `:227-238` | main prints `validated pins: …` as line 1; `json.loads` raises |
| (d) refusal naming the absent default | `:240-246` | main installs successfully, rc 0 ≠ 2 |
| (c) failed preflight refuses install **and** render | `:248-274` | no preflight exists on main; `arm_readiness` was lazy there, so `from scripts.run_night import DEADMAN_HOUR` still succeeds and the install proceeds rc 0 |
| (e) uninstall, no python/venv/driver modules | `:380-401` | main's unconditional `DEADMAN_HOUR` subshell (`from scripts.run_night import …`) cannot import from the fixture dir → empty `read` → non-zero under `set -e` |
| (f) preflight JSON, no custody, no process | `test_run_night.py:254-275` | no `preflight` subparser on main → argparse rc 2 |
| (g) each formerly-lazy import blocked | `:277-301` | rc is non-zero on main, but from argparse; `assertIn("ImportError: missing preflight dependency: …")` fails |
| (h) `MIN_PYTHON` == `requires-python` floor | `:303-308` | `self.driver.MIN_PYTHON` does not exist on main → `AttributeError` |

The test-(b) trick is honestly commented (`:186-187`, *"the real interpreter still parses/runs the probe"*). **NIT** — because the fake is really Python 3.14 with a spoofed `sys.version_info`, it does not exercise `ast.parse` under a genuine 3.9, which is the one place a future 3.10+-only syntax addition to `run_night.py` would turn the friendly refusal into a SyntaxError traceback. I closed that gap by hand this session (real `/usr/bin/python3` 3.9.6: parse OK, exact refusal line, rc 2). Cheap hardening: a `@unittest.skipUnless(Path("/usr/bin/python3").exists())` case pinning the real-3.9 message.

**NIT** — `tests/test_run_night.py:869-885`, the template-invariant test, still asserts `@@HOUR@@`, `@@PATH@@`, `@@COURIER_BIN@@`, `RunAtLoad/false` etc. but was not extended with `assertIn("@@PYTHON@@", template)` / `assertNotIn("/usr/bin/env", template)`. The new placeholder is locked only indirectly, via the rendered plists in the installer tests. One line would make the template's own invariant test complete.

### Req 6 — docs: **PARTIAL**

Substance is right and both quoted install commands gained the interpreter: `derivation_night_runbook.md:1304-1305` (`--python "$PY"`) and the §-index row at `:2160`. The uninstall commands correctly did **not** gain it (`:1351-1352`, `NIGHT_HANDBACK.md:130`). The 02:56 worked example is concrete in both files (date, time, `Python 3.9.6`, `datetime.UTC`). Three pedagogy defects against the binding writing standard:

**SHOULD_FIX — `NIGHT_HANDBACK.md:158`, `--render-only` is used with no gloss and is never explained in that document.**
`grep -n "render-only" docs/process/NIGHT_HANDBACK.md` returns exactly one hit, the new line 158: *"Install and `--render-only` default to `<measurement_root>/.venv/bin/python`"*. A reader of this file alone cannot act on it — nothing here says `--render-only DIR` writes the two plists into `DIR` without installing them, which is precisely the D-175 validation step. Fails the first-use test: built, glossed, or deleted. (`LaunchAgent` at `:165` and `driver preflight` at `:166` *are* glossed at first use — bench-verified, those are the first occurrences of each string in the file — and `venv` is glossed at `:156-157` before its first bare use. Those three pass.)

**SHOULD_FIX — `derivation_night_runbook.md:1305` uses `--python "$PY"` 22 lines before the paragraph that explains it (`:1327-1337`).**
The zsh block runs 1272→1325; the explanation starts at 1327. The standard's clause is explicit: *"No word does unpaid work … restructure so the definition precedes the use."* An operator working the block top-to-bottom meets the new flag cold. Cure: move the paragraph above the block, or add one comment line at `:1304` (`# --python pins the driver interpreter; see the paragraph after this block`).

**SHOULD_FIX — `derivation_night_runbook.md`, "driver preflight" is introduced but never enters the glossary the file maintains.**
`preflight` already appears at `:153`, `:562`, `:688`, `:1048`, `:1067`, `:1135` (all meaning the *chain/input* preflight) long before `:1330` introduces `**driver preflight**`. The compound term is correctly glossed at its own first use, so the first-use test passes — but the file's own convention is a glossary table carrying every term (`:2218` dead-man, `:2225` `$PY` / project venv interpreter, `:2245` pre-settle allowance, `:2249` Δ), and the two preflight senses are now one letter apart in a document that already tables `chain preflight` and `input preflight`. Add a `| driver preflight | §1.4 | … |` row distinguishing it from the chain/input preflight.

**SHOULD_FIX — `NIGHT_HANDBACK.md:160-161` ships an unqualified escape hatch.**
*"A stub checkout needs that venv **or an explicit compatible interpreter with the driver's imports available**."* "Compatible" and "the driver's imports available" are the load-bearing words and are unexplained — a reader cannot tell whether a bare Homebrew 3.13 qualifies. It does today (the seat's V3 ran the preflight green under `/opt/homebrew/opt/python@3.14/bin/python3.14`, i.e. the driver's module graph is currently stdlib-only), but that is a property of today's imports, not a promise. Say the testable thing: *"any Python ≥ 3.11 that passes the preflight — which is what the preflight is for."*

**NIT** — the four new installer refusals (`invalid --python:`, `interpreter … reports Python …; minimum is …`, `missing executable interpreter:`, `cannot derive measurement_root…`) are in no refusal table. The runbook tables chain launch-time refusals exhaustively (`:2010-2024`) but has never tabled installer refusals, so this is a pre-existing asymmetry, not a regression.

---

## 3. Kernel / state consequences — **yes, a row is required before any arm**

Read: `docs/process/state_kernel.json` `/tasks/NIGHT-REHEARSAL-01`, and D-175 at `docs/decision_log.md:11424-11441`.

1. **The kernel's pending dependency is written as if the night merely has not been harvested yet.** `state_kernel.json`, `NIGHT-REHEARSAL-01` dependency `REHEARSAL-20260911-HARVESTED`, `"state": "pending"`, `"evidence": null`, required text: *"rehearsal-20260911 … **fired and harvested**: receipt not refused (item 6) and the pre-night 07:00 dead-man stand-down observed with nothing written into `night/` (item 5)"*. It did not fire — it died on `ImportError` before any gate — and the 07:00 dead-man refused `agent_present`. Both acceptance items 5 and 6 are **unmet and un-attemptable from this plan**, not pending harvest. The dependency text needs a dated correction; otherwise a future reader (or a headless magistrate) reads "pending" as "go collect the results".
2. **There is no row for the cure itself.** Nothing in the kernel names NIGHT-INTERPRETER-PIN-01 or makes it a hard dependency of the next stub arm. It must be one: the next `REHEARSAL_STUB` cannot be armed on the old code without repeating the crash, and it cannot be armed on the new code using runbook 67 as written (§1.2). Suggested shape: a `task`-kind hard dependency `NIGHT-INTERPRETER-PIN-01` on `NIGHT-REHEARSAL-01`, `scope: start`, satisfied by this PR's merge commit, **plus** the runbook-67/D-175 `--python` cure as a second, separately-evidenced condition.
3. **`NIGHT_HANDBACK.md` §Executed needs the 09-11 row.** §Executed (`:83`) currently holds only the 2026-09-09 history. The 09-11 crash, its cause (`joulewise/arm_readiness.py:26` `from datetime import UTC, datetime` under `/usr/bin/python3` 3.9.6), the courier email id, and the disposition of the stub checkout and plan root belong there, in the same shape as the 09-09 entry — that is what makes §Purpose / §Where the results are / §Next lane safe to rewrite for the *next* night and resolves §1.3.
4. **D-175 condition 2 needs a dated addendum** (`docs/decision_log.md:11436`): the ruled `--render-only` validation step now requires an interpreter argument for any stub whose `measurement_root` has no `.venv` — which is every `/private/tmp` detached stub root D-175 explicitly blesses.

None of items 1–4 is a defect of the seat; all four are merge-adjacent bookkeeping the lead owns, and items 1–3 gate arming.

---

## 4. Findings index

| # | Severity | Location | One line |
|---|---|---|---|
| F1 | **BLOCKER (arming) / SHOULD_FIX (merge)** | `67-arm-runbook-rehearsal-20260911.md:173,252`; `decision_log.md:11436` | The arming procedure of record omits `--python` and now exits 2 from a venv-less stub checkout |
| F2 | SHOULD_FIX | `NIGHT_HANDBACK.md:44-45,57-59,104-105,115-122` vs `:163-165` | Same file says the night crashed and that its results await harvest |
| F3 | SHOULD_FIX | `pack_night_go_receipt.md:637`; `67-arm-runbook…:192,197,441` | `install_night_agent.sh` line pins shifted by ~40 lines |
| F4 | SHOULD_FIX | `install_night_agent.sh:5,29` | Usage string advertises `[--python]` and `[--uninstall]` as independent, then hard-refuses the pair with a bare usage dump |
| F5 | SHOULD_FIX | `NIGHT_HANDBACK.md:166-167` | "runs the driver's imports" over-promises; lazy imports inside `joulewise` (`arm_readiness.py:3833,5624,8052`) stay uncovered |
| F6 | SHOULD_FIX | `NIGHT_HANDBACK.md:158` | `--render-only` used, never glossed or built in that document |
| F7 | SHOULD_FIX | `derivation_night_runbook.md:1305` vs `:1327` | `--python "$PY"` used 22 lines before it is defined |
| F8 | SHOULD_FIX | `derivation_night_runbook.md:2218-2250` | New term "driver preflight" missing from the file's own glossary, beside two other "preflight" senses |
| F9 | SHOULD_FIX | `NIGHT_HANDBACK.md:160-161` | "an explicit compatible interpreter with the driver's imports available" is untestable as written |
| F10 | SHOULD_FIX | `state_kernel.json` `/tasks/NIGHT-REHEARSAL-01`; `NIGHT_HANDBACK.md:83` | Kernel dependency presumes the night fired; no row for the cure; §Executed has no 09-11 entry |
| F11 | NIT | `scripts/run_night.py:40-43` | Dead-man now shares the run path's import graph; safety-net independence traded for preflight coverage |
| F12 | NIT | `scripts/run_night.py:1881`; template `:9-15` | Hoisted imports write `__pycache__` at night; harmless (gitignored, `--porcelain` unaffected); `-B` would close it |
| F13 | NIT | `install_night_agent.sh:148` | `env -i` omits `TMPDIR`/`USER`/`LOGNAME` that launchd injects — stricter, not laxer; worth a comment |
| F14 | NIT | `tests/test_install_night_agent.py:184-203` | Fake 3.9 is really 3.14; the genuine-3.9 `ast.parse` path is untested (verified by hand this session) |
| F15 | NIT | `tests/test_run_night.py:869-885` | Template invariant test not extended with `@@PYTHON@@` / `NotIn /usr/bin/env` |
| F16 | NIT | `12-arm-runbook-68-g2a-20260912.md:496,651` | Real-night runbook relies on the venv default without saying the venv is now load-bearing at install time |

No finding contradicts the seat's report; its `status: blocked` was a sandbox staging failure only, and the lead's commit `17c26a1a` carries all seven files.

---

## 5. Summary judgment

The contract lens finds **no promise broken by the code**. No `docs/contracts/*.md` clause pins the plist argv, `/usr/bin/env python3`, or the installer's flag set, so no ruling was owed and none was skipped; the change moves the night installer onto the interpreter-pinning discipline `MAGISTRATE_WATCHDOG.md:175` already requires of its sibling. All six numbered requirements are implemented, two of them (the AST-read of `MIN_PYTHON`, the module-scope version guard) more strongly than specified, and every new test is defect-shaped. The residual risk is entirely documentary and entirely outside the seat's WRITE_SCOPE: the runbook and decision-log text that operators and the headless magistrate actually execute has not caught up with the new required argument, and the kernel still describes a night that never ran as merely unharvested. F1, F2 and F10 must land before an arm; F3–F9 before the lane is called closed.

VERDICT: MERGEABLE AFTER FIXES
