# A173 implementation brief — ARM-CENSUS-IDLE-INTERACTIVE-01

Design seat, 2026-09-15. Advice for the magistrate; no implementation or test execution occurred in this seat. The recommendations below require the rulings in part 6 before delegation to an implementer.

## 1. Goal, authority and acceptance

Implement D-180 clause 3 at the **arm-time census**, the process inventory checked before publishing a night plan and installing its jobs. Only a validated `REHEARSAL_STUB` plan may disregard an otherwise foreign interactive Claude/T3 session, and only after inspecting every descendant for test, measurement or capture work. Keep the **plan-span census**, the unfiltered agent check used during the reserved agent-free interval, unchanged. The plan span begins at `t0 − 25 minutes`; `t0` is the planned measurement start.

Authority read in order:

1. `TASK_QUEUE.md:795` / A173 and `docs/process/state_kernel.json#/tasks/ARM-CENSUS-IDLE-INTERACTIVE-01/acceptance`. Acceptance, verbatim: “Runbook step-3b preconditions classify an interactive session as not foreign only when its process tree holds no test, measurement, or capture child; REHEARSAL_STUB only; plan-span refusal night_refused_agent_present untouched and pinned by a counterfactual test; refuters on the classifier.”
2. `docs/process_traces/2026-09-09-rehearsal-harvest/121-ed-rulings-2026-09-10-recoverability-steerability.md:9–23,41–46`: the three proposals and Ed's “1, yes to all 3”, plus the explicit arm-only limit. `docs/decision_log.md:11757–11771` records clauses 2 and 3 in operational terms.
3. `docs/process_traces/2026-09-13-activation-24b9d3dd/55-ed-directive-337-verbatim.md:9–15`: D-181 preserves the census and other soundness fences and orders INSTALL-WINDOWS-MULTI-01 → ARM-RETRY-CLASS-01 → this lane. Design was explicitly requested while A173 remains blocked on its predecessor; this brief does not release implementation or arm anything.

Workspace inspected: `design/2026-09-15-arm-lanes-b`, not the prompt's descriptive “main”; at entry HEAD and origin/main were both `84e577ac97572f28740d22d63be111560401aebf`. Clean at entry. The supplied manifest's canonical SHA-256 and HEAD were verified against the supplied digest. No active stop card. Current seat's exhaustive write authority is this brief alone. At final inspection local HEAD remained unchanged and origin/main had concurrently advanced to `62131e5993bb4576c34f7e7690bcb0f8363bde39`; this seat neither fetched nor changed refs. The baseline scope check reported `SCOPE_OK`, with only this brief modified.

The future base is the read-only installer checkout `/Users/edr/code/JouleWise-wt-iw-txn`, branch `feat/2026-09-15-install-windows-transactional`, inspected HEAD `0ba6ce54fa08d52da1c6124ff33e1c69a6f312fa`. It was clean on the first inspection, then acquired concurrent edits to its runbook, handback and `tests/test_night_agent_install.py`. The following working-file hashes identify the later inspection, not a promise about its eventual merge:

| File in installer checkout | SHA-256 |
|---|---|
| `docs/phase_2/derivation_night_runbook.md` | `58ef3272237243917d87bb28a263f842009796d15f3ad2abcf7360591775858c` |
| `docs/process/NIGHT_HANDBACK.md` | `b5cf345ab0a681627069eef17eaac402e3e0f1795081340317afe929bf814489` |
| `joulewise/night_agent_install.py` | `756fe0f0dd530caee8e9ec99afe11f1185ce2e1e02d99c410d92d37383b4273f` |

The lead must refresh anchors on the landed installer and retry-lane heads before issuing implementation WRITE_SCOPE. No concurrent changes were edited here.

### Findings that determine placement

- `scripts/magistrate_watchdog.py:370–378` calls `agent_census(make_probes())` directly in `production_census()` (installer base: line 379). It has **no own-process or headless exemption**. Its callers include the active-span and post-kill decisions. Changing it would change plan-span behavior.
- `_is_interactive_claude()` at main line 872 (installer base line 907) rejects `-p`, `--print*`, daemon, spare and pty-host forms. It is an interactive-owner/handoff recognizer, **not a production-census filter**. `handoff_census()` at main line 959 explicitly says `"Handoff ownership only; never substitute this for the night agent census."` Neither is the new policy seam.
- Headless arming is possible because the separate runbook precondition excludes the *proven arming activation and attached descendants*. The historical stub runbook `docs/process_traces/2026-09-11-activation-58a3bcfc/13-arm-runbook-stub-20260912.md:197–234,482–540` proves its owner PID is an ancestor of the census process, then classifies raw hits by ancestry. Thus the own `claude -p` can pass **that check**, while a foreign `claude -p` must not pass. Do not add a global headless exclusion.
- The pending installer `validate_install()` checks plan validity, age, checkout pins, driver preflight, schedule, existing records and admission. It does not implement an agent census. Its `Transaction.run()`/`_commit()` owns installation and recovery. Adding an implicit census there would broaden this lane into a new installer admission contract. Recommend an explicit arm command in the runbook, with a class guard inside the command's classifier.
- The current reusable arm procedure is runbook §0.6 and §1.4. The search for `runbook template`, `step-3b`, and `step 3b` found historical copied stub procedures (21b, 67 and 13), not a separate current generator/template for this check. Keep those records immutable. §1.4 currently has a diagnostic `ps … | grep … || true`; it does not enforce the documented no-foreign precondition. Replace it with the coded check.
- Runtime detail: `night_gate.evaluate_night()` refuses an agent hit before its rehearsal-class branch. Nevertheless `run_night()` deliberately continues a built-in harmless stub for rehearsal plans and observes, rather than kills on, subsequent hits (`abort_on_census=not rehearsal_effective`). `tests/test_run_night.py:test_rehearsal_census_hits_are_observed_without_killing_the_stub` pins this. Preserve it; do not describe a recorded rehearsal refusal as proof that the stub never ran. Real plans must continue to refuse before chain launch.

### Clause map for the implementation handoff

These are proposed test names/sites, not executed assertions. The implementation return must replace symbol anchors with final `file:line` references and report the actual mutant results. A **mutant** is an intentional one-site defect used to prove that a test can detect the failure it claims to cover.

| Authority proposition | Production site proposed/preserved | Biting assertion | One-site counterfactual |
|---|---|---|---|
| D-180 cl.3 “For REHEARSAL_STUB plans only” (`docs/decision_log.md:11767`) | `joulewise/arm_census.py:classify_arm_census`, exact parsed-class branch | C02: same idle tree passes stub, fails diagnostic and pack | M02: unconditional idle exemption |
| “interactive `claude`/T3 session” (same entry) | `interactive_root` using executable/arguments, not an arbitrary occurrence of a name | C03/C04: permitted roots and rejected lookalikes/headless/desktop cases | M03: accept any command containing an agent name |
| “no child test, measurement, or capture process” | full descendant closure plus `classify_descendant` | C05–C09: direct/grandchild/wrapper/fixture work all blocks | M05–M09: direct-child-only walk, omit workload family, ignore fake paths, or allow unknown work |
| “arm-time … only”; “plan span is unchanged” (`121…md:43–46`) | arm command's time check; existing `agent_census`, watchdog `production_census`, driver first census and running census | C10, C14–C18: boundary refusal and actual old-path observations | M10: permit at span start; M14–M18: filter a production site or suppress a real-plan abort |
| D-181 “census at arm and at t0” (`55…md:11`) | `scripts/run_night.py:main(arm-census)` and live runbook §1.4 before publication | C12/C13: parsed plan controls check; nonzero result prevents publication | M12/M13: trust caller's class or ignore census failure |
| D-180 cl.2 plan-span/evidence refusals retain existing treatment (`docs/decision_log.md:11761–11764`) | no change to retry classifier or night reason-code registry | C14/C16: exact `night_refused_agent_present`, same evidence and no real chain | M14/M16: rename, hide, or turn the receipt into GO |

## 2. Proposed implementation WRITE_SCOPE — exact and exhaustive

This is a proposed allowlist for a *future* lead-issued implementation prompt; it grants this design seat no additional writes.

```json
[
  "joulewise/arm_census.py",
  "scripts/run_night.py",
  "tests/test_arm_census.py",
  "tests/test_night_gate.py",
  "tests/test_run_night.py",
  "tests/test_magistrate_watchdog.py",
  "docs/process/NIGHT_HANDBACK.md",
  "docs/phase_2/derivation_night_runbook.md"
]
```

No production change to `joulewise/night_gate.py`, `scripts/magistrate_watchdog.py`, `joulewise/night_agent_install.py`, or `scripts/install_night_agent.sh`. The installer read was necessary to avoid inserting a second transaction gate or breaking its system-Python uninstall path. Lead bookkeeping, state-kernel updates and the eventual implementation report need separately enumerated lead-owned paths; they are not silently included here.

## 3. Per-file dictated edits, with anchors

### 3.1 New `joulewise/arm_census.py`

New file; no existing lines to replace. Give it the module docstring `"""Read-only pre-publication arm census; never a night gate probe."""`. Keep a pure classifier separate from observation. Proposed public seam: `classify_arm_census(plan, observation, *, owner, caller_pid, now_epoch_s)` and `observe_arm_census(plan, *, caller_pid, owner_override=None)`. Neither signals, sleeps, launches work, reads measurement artifacts, creates directories, or writes receipts. Return a structured verdict with `pass`, `reason`, parsed `receipt_class`, plan ID/hash, observed time, raw probe result, own rows, exempt interactive roots, foreign rows and observation errors. Each exemption retains root PID/start identity, descendant identities and classifications. A diagnostic JSON record is evidence of this check, not a GO receipt or reusable authorization token.

**Observation and failure behavior.** Use the existing `SysctlDarwinProcessReader.inventory()` and `read_exact()` APIs from `joulewise/quiet_guard_process.py` without changing that module. The kernel inventory supplies PID, PPID and start identity; `read_exact` supplies true executable and argument-vector values and rejects identity changes. PID means process identifier; PPID means the process identifier of its parent. A start identity distinguishes an old process from a later process assigned its number. Do not import the watchdog's `RealProcessTable`: it silently skips malformed text rows, which cannot prove absence of work. Do not split a display command string to infer an executable or parse shell quoting as if it were a true argument vector.

Recommended arm-only discovery under R1: `ARM_DISCOVERY_ARGV = ("/usr/bin/pgrep", "-ilf", "codex|claude|t3")`. The `i` makes the *arm* inventory case-insensitive so `T3 Code` roots are visible. Never modify `night_gate.AGENT_CENSUS_ARGV`, which remains exactly `("/usr/bin/pgrep", "-lf", "codex|claude|t3")`. Record the arm argv and raw output explicitly. Accept probe exit 1 only with empty stdout, or exit 0 with well-formed nonempty hit lines. Any other combination, exception, malformed PID line, duplicate hit, missing inventory row or exact-read failure produces `arm_census_unknown`, a nonpassing observation. Do not silently drop a hit that disappeared between observations.

For every hit, observe the ancestry needed to identify a permitted interactive root, plus the owner/caller ancestry. Enumerate *all* descendants from the accepted kernel table, including commands whose names contain no agent substring. Read their exact arguments. Read the relevant identities again before returning; take a final inventory and refuse if the relevant trees gained or lost members or changed links/start identities during the check. This final comparison is a new arm-check safeguard, not a modification of quiet-guard recovery's one-snapshot contract. One failed observation ends the invocation; no retry loop. A snapshot cannot prevent a process starting work after it returns: run the check immediately before publication and retain the independent plan-span checks.

**Own activation.** Default owner comes from `<custody-parent>/magistrate/magistrate.lock`, using the existing schema/PID/start-token format. Prove the recorded start token against the live process and prove the root is an ancestor of the *current census caller*. The watchdog lock's `lstart` string and the kernel start token have different formats: compare the lock against a targeted `ps -p PID -o lstart=` observation bracketed by exact kernel-identity reads; never compare these two token formats directly. An explicit `--owner-pid` override, for a foreground armer that does not own the lock, is allowed only with a nonempty `--owner-reason`, a live agent-session root, and the same ancestry proof; acquire and record its current start identity. PID 1, a generic shell/terminal ancestor, a stale/reused PID or an unrelated activation cannot be designated owner. No missing-lock fallback to “all headless agents are own”.

Preserve the own-activation exception for all plan classes. Exempt its root (including `claude -p`) and required foreground census corridor, but inspect attached side branches for active seats/tests/captures; step 3b still requires stopping own work. Identify the census corridor as the exact ancestry from the census PID to the owner. Exempt the executing `run_night.py arm-census` invocation and that corridor only from the workload classifier, not a sibling `run_night.py run`. Reject daemon/spare/resumed-twin machinery even if attached. Foreign headless sessions never inherit the own exception.

**Class and time checks.** Read the plan bytes once, parse them with `NightPlan.from_mapping`, retain their SHA-256, and pass that parsed object into the classifier. No `--class`, `--stub`, `--allow-idle`, environment toggle, plan-ID substring, test path, or `--rehearsal` flag may select the exception. Precisely `plan.receipt_class == "REHEARSAL_STUB"` enables interactive exemptions. Other valid classes get only the existing own-activation treatment. Malformed/unknown classes fail plan parsing. Refuse `now_epoch_s >= plan.t0_epoch_s - PLAN_LEAD_S` as `arm_census_outside_arm_time`. The constant's existing owner is `scripts.magistrate_watchdog`, not a module-level export from `run_night`: the pending driver's `install_close_epoch()` imports it locally. At the CLI boundary obtain the same span start as `install_close_epoch(plan) + INSTALL_CLOSE_MARGIN_S`, and pass that internally derived boundary into the classifier; never accept it as a CLI override. This reuses the pending implementation without another literal or a new watchdog import in the classifier. Existing install-close and span checks remain stricter separate requirements; a census pass does not override them.

**Interactive roots.** Match executable identity and launch arguments. Recognize a Claude executable named exactly `claude` or the existing `/claude/versions/<major>.<minor>.<patch>` shape. Reject print/headless forms (`-p`, attached `-p…`, `--print`, `--print=…`), daemon, spare and pty-host roles, and the `--reply-on-resume` resumed-twin form. Do not reuse `_is_interactive_claude` as a general allow rule: its looser text matcher serves a different contract. `echo claude`, a script under `.claude/`, and `notclaude` do not qualify.

Recognize the T3 main executable at `/Applications/T3 Code.app/Contents/MacOS/T3 Code`, and a Node-launched T3 command whose script argument ends in `/t3-code/dist/cli.js`; both shapes are documented in the earlier arm refuter records (21e5/21e6). The Node process's actual script operand, not any later string, must match. Reject `exec`, `run`, `-p` and `--print` execution forms. These are structural session candidates, not proof of user inactivity. An empty descendant workload set is the definition of “idle” for this lane; CPU percentage, terminal attachment and HID activity are not substitutes. A standalone interactive Codex CLI is not included in D-180's enumerated Claude/T3 exception without a further ruling.

**Descendant closure and classification.** Build a parent-to-children index; walk until no new PID is found. Include grandchildren through shells, transports and other intermediates. Reject cycles, missing required ancestors and ambiguous/reused identities. For each candidate root, evaluate the entire tree before exempting *any* of its raw agent hits. Work in a sibling branch of a root must invalidate the whole root. An orphan is never attributed to a former parent by filename, model name or a saved PID; independently observed raw orphan hits remain foreign. Historical detached-work cleanup stays a separate precondition.

Use these categories in priority order: `workload` → `agent_execution` → specifically recognized idle transport/helper → `unclassified`. The first, second and last block an exemption. Known workload rules give useful reasons; the unclassified fallback prevents an omitted future runner from being silently treated as idle. Do not whitelist an entire process subtree because its root is interactive.

| Executed command family to reject in descendants | Exact recognition rule / repository evidence |
|---|---|
| Standard-library tests | Python interpreter with `-m unittest` (including dotted unittest module), executable `unittest`, or executed Python script named `test_*.py` / `tests/**`; include interpreter flags before `-m` or the script. `tests/test_night_gate.py`, `tests/test_run_night.py` and the canonical suite use unittest. |
| Other test runners | Executable `pytest`, `py.test`, `pytest-<version>`, or Python `-m pytest`; executed `scripts/shard_tests.py` in parent and worker modes. Match executor position, not a filename passed to `cat`. |
| Native telemetry | Executable basename `powermetrics` or `nvidia-smi`, including interpreter/wrapper descendants. Never exempt merely because the row runs as root, has no CPU usage, or is waiting. |
| Night/campaign/capture entry points | Executed `scripts/run_night.py` in every mode other than this exact active arm-census caller; `scripts/run_campaign.py`; `scripts/validate_powermetrics_fiducial.py`; `scripts/capture_t0_step.py`; `scripts/rehearse_t0_unattended.py`; `scripts/spike_mlx_prompt_cache.py`; `scripts/night_chains/calibration_derivation_only.zsh`; a executed `chain.zsh` wrapper. Conservative classification includes driver preflight/schedule descendants; the runbook does them before this check. |
| Repository measurement module runners | Python `-m joulewise` and its submodules unless the exact command is this census implementation; executed `joulewise/adapters/node_worker.py` or `-m joulewise.adapters.node_worker`. Any unlisted Python script/module remains unclassified and cannot earn an exemption. |
| vLLM / MLX serving and measurement fixtures | Executable/script operand basename `vllm` with `serve`; Python `-m vllm…` / `-m mlx…`; executed `tests/calibration_exits_fixtures/fake_sampler.py` and `fake_mlx_core.py`. `joulewise/adapters/node_worker.py:_vllm_serve_command` and `tests/test_node_worker_subprocess.py:_write_fake_vllm` establish that a Python-script `…/bin/vllm serve /fake/model …` is a real child. `/tmp`, `fake`, `mock`, `fixture` and `/fake/model` never confer exemption. |
| Delegated/headless agent work | Executed `codex exec` or `codex e`, including options before the subcommand; any Claude print/headless invocation; another unrecognized agent worker. A nested interactive agent candidate is not inert transport: classify it recursively or refuse, never skip it. |
| Launch wrappers and opaque commands | `env`, `sudo`, `nice`, `nohup`, `caffeinate`, shell `-c`/`-lc`, Python `-c`/stdin and unknown launchers block while alive, except the proven owner's census corridor. Do not implement a partial shell parser that can turn `sh -c 'sleep 1; pytest'` into an idle shell. The full tree still catches the workload after its wrapper exits. |

The deliberately small inert set proposed under R1 is: a plain waiting shell without `-c` or a script operand; a `sleep` process; `codex mcp-server`; `codex app-server` only beneath a proven T3 root; and a Node process executing this checkout's exact `scripts/codex-app-bridge.mjs` or `scripts/claude-bridge-mcp.mjs`. These transports merely hosting a connection can be inert only if their own complete descendant closure is clear. Foreign ChatGPT/Claude desktop helpers, `codex-code-mode-host`, arbitrary `node`, arbitrary Python, a Claude daemon/bg-spare/bg-pty-host, and unknown T3 Electron helpers remain unclassified/foreign until a lead-adjudicated exact shape is added with both positive and busy-descendant tests. This first implementation is intentionally not a blanket desktop-app exemption. T3 helper coverage remains PROVISIONAL until a non-measurement observation identifies its actual tree; see R1.

### 3.2 `scripts/run_night.py`

Pending-base anchors at `build_parser()` / `main()`:

```python
    subcommands = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "dead-man", "rehearse"):
```

```python
    args = build_parser().parse_args(argv)
    if args.command == "schedule":
```

Add a separate `arm-census` subcommand with required `--plan`, optional paired `--owner-pid` / `--owner-reason`; require both or neither. Dispatch it before `schedule` using a lazy import of `joulewise.arm_census`. Resolve and read only the requested staged/published plan; no default plan discovery. Print the structured observation to stdout and return 0 for pass, 3 for a known foreign/busy process, 2 for invalid plan/ownership/time/observation. Retain the diagnostic reason names `arm_census_foreign`, `arm_census_unknown`, `arm_census_owner_invalid`, `arm_census_outside_arm_time`; they are local pre-publication reasons, not entries in the night gate's reason registry. No receipt/result/chain/courier/launchd effects, even on failure. Include the observed plan hash in output; do not accept saved JSON as a substitute for a new census.

Keep byte-for-byte logic at these anchors: `initial_probe, initial_refusal = agent_census(probes)`, `_run_chain(... abort_on_census=not rehearsal_effective)`, the pack initial-census refusal, `dead_man`'s census, and every existing `run`/`rehearse`/`dead-man` dispatch. Do not pass an “arm” flag into `agent_census`. Do not add the new module to the installer's system-Python import path or preflight's promised module list.

### 3.3 Tests: new `tests/test_arm_census.py` and existing test files

New file: create `ArmCensusTests` with injected immutable process rows, exact argument tuples, fake clock, fake lock reader and fake kernel/pgrep readers. No real census, sleeping process, fake server, subprocess test runner, OS signals, launchctl or measurement invocation. Literal strings describing fake vLLM suffice. Test expected literal PID sets and reasons; never derive expected values from production match tables. The separate C13 documentation-wiring test is the only proposed small shell execution, and waits for the lead's explicit test release like every other test.

`tests/test_night_gate.py`, append beside existing anchor:

```python
    def test_a_census_that_finds_lines_refuses_and_preserves_them(self) -> None:
```

Add C14/C15 to `NightGateTests`, using `FakeProbeSource`, `make_plan()` and actual `evaluate_night()`. Pin raw evidence, reason and condition C3, not just any nonzero return. Do not change existing expected outcomes.

`tests/test_run_night.py`, append near:

```python
    def test_refusal_writes_receipt_and_refusal_without_spawning_chain(self) -> None:
```

Add C12/C13/C16/C17 with the existing injected probe/spawn/courier seams. For packs, extend near `test_first_census_refusal_prevents_preparation_and_arm`. Preserve and retain C18's existing anchor `test_rehearsal_census_hits_are_observed_without_killing_the_stub`.

`tests/test_magistrate_watchdog.py`, append a fixture-only `ArmIsolationTests` class beside `ClaudeHostIdentificationTests` and `HandoffDefectTests`. Add C19, calling the actual `production_census()` with `make_probes` patched; no watchdog launch, state-directory writes or real process query. Keep the existing versioned-child/headless exclusion tests.

### 3.4 `docs/phase_2/derivation_night_runbook.md` — pending installer base

Anchor §0.6:

> Before the arm census, stop all own seats, delegated tasks and background jobs
> using the activation's real task controls; record the task IDs and results and
> invent none. Then inspect and classify by ancestry:

Replace the following diagnostic grep and the old blanket interactive-session sentence with the following text (subject to R1–R3). Retain the paragraph's prohibition on signaling foreign processes and the separate desktop-app/plan-span instructions.

> **Step 3b — stop own work and check the arm-time process inventory.** An arm publishes the plan where the supervisor can find it, then installs the two jobs that will run the night and report it. A census is an inventory of running processes. A process's PID is its numeric identifier; its PPID identifies its parent. Its process tree includes children, grandchildren and every later generation reached through those parent links. “Own” means the current arming activation, identified by its recorded PID and start time and proven to be an ancestor of the process performing this check; an older activation or a process detached from its parent is not own.
>
> Stop this activation's delegated seats, tests and background work with their real task controls, and record the results. Run `arm-census` below after the plan is staged, and again immediately before publication. Staging means the plan exists outside the supervisor's plan-discovery directory. The command reads that exact plan and prints its SHA-256, a digest identifying the bytes checked, together with the inventory and each classification. Only exit code 0, the integer success result, permits the next arm step. Any other exit stops publication; preserve its output and do not signal foreign processes.
>
> For `REHEARSAL_STUB`, the plan class using the driver's built-in harmless substitute chain, a foreign interactive Claude or T3 session may be classified as not foreign at this check. Interactive means a recognized session host, rather than a print-mode agent, delegated worker, daemon or background resume host. Idle here means its entire process tree has no test, measurement, capture, headless agent or unclassified child; it does not mean low CPU usage or merely an open terminal. The command examines descendants through shells and connection-hosting helpers. A Python unittest/pytest runner, a test shard runner, powermetrics, a night/campaign/capture program, a `codex exec` worker, or a vLLM/MLX process blocks the exception. A fake vLLM server is still a process and also blocks it. An unreadable or changing tree stops the check. The exact recognized commands and helper cases are defined in `joulewise/arm_census.py`; its diagnostics name the blocking PID and category.
>
> `DIAGNOSTIC_NO_PACK`, the real night class without a measurement pack, and `TRANSACTION_PACK`, the real night class bound to a measurement pack, receive no idle-session exception. The current arming activation's proven ownership is a separate existing exception; it is not a rule excluding all `claude -p` processes. Here `-p` selects Claude's noninteractive print mode. Another activation in that mode remains foreign.
>
> This command checks one observation before publication, not future inactivity. Close all agent sessions and quit agent desktop apps before the plan span, the reserved agent-free interval beginning 25 minutes before `t0`, the planned measurement start. The check itself refuses at or after that boundary. At `t0` the night gate still uses its unfiltered census and records `night_refused_agent_present` when it finds an agent. A real measurement chain does not start on that refusal. A rehearsal may still execute its existing harmless substitute and record census hits; this change gives no permission to keep an agent open during the plan span.

Use this command at the initial check after staging and at the final check in §1.4; this runbook's actual diagnostic plan remains diagnostic, with no class change:

```zsh
"$PY" -B scripts/run_night.py arm-census --plan "$STAGED_PLAN"
```

Gloss the variables immediately before the first command: `$PY` is the measurement checkout's Python interpreter; `$STAGED_PLAN` is the absolute path of the staged plan; run from the measurement checkout containing the reviewed code. For an armer that is not the lock's recorded owner, document `--owner-pid <current-session-pid> --owner-reason '<why the lock does not name this session>'`, explain how to identify the current session from its parent chain, and state that the command must prove this relationship. Never prescribe a guessed PID.

Anchor §1.4:

```zsh
# 4. The final raw census, immediately before publication (§0.6).
ps -axo pid,ppid,command | grep -E 'claude (daemon run|bg-spare|bg-pty-host)|--resume' || true

# 5. Publication: the one irreversible instant.
```

Replace step 4 with the new command and an explicit shell stop on nonzero (`if ...; then ...; else ...; exit "$rc"; fi`, capturing the failing status immediately). Do not rely only on prose, `|| true`, or a pipeline that loses the command's exit status. Name it “arm-time census”; record stdout/stderr in the arm transcript. Place no lengthy work between this check and the existing `os.replace` publication. Keep the class assertion in step 3 (`assert plan.receipt_class == 'DIAGNOSTIC_NO_PACK'`), schedule arithmetic, notice evidence, directive/NO checks, both install commands and transactional recovery unchanged. For a future stub arm, its own reviewed staged plan and coordinates use the same command; do not reuse this diagnostic runbook's frozen nightly values as a stub plan.

Anchor §1.3: `Existing plan-age and census gates still apply.` Add one sentence: “The arm-time census is the pre-publication process check in §0.6; its rehearsal-only exception changes neither the install close nor the agent-free plan span.” Update the first-use table's existing census row and add arm-time/interactive/idle/PPID entries with the definitions above. Update the fact-table reference to the new command. All newly dictated prose must retain these first-use definitions; `arm`, `census`, `own`, `tree`, `idle`, `interactive`, class names, `t0`, plan span, PID/PPID, staging, exit code and digest must not appear first as unexplained shorthand.

### 3.5 `docs/process/NIGHT_HANDBACK.md` — pending installer base

Insert a standing section **Arm-time census for rehearsal plans** after the live-template timing update and before the anchor `## Purpose of this night`. Do not rewrite any Executed section, dated arm record or retained historical precondition. Dictate:

> An **arm** publishes a plan and installs the jobs that will execute and report it. Its **census** is the inventory of running processes checked immediately before publication. The live procedure is runbook §0.6 step 3b and §1.4: stop the arming activation's own work, then run `scripts/run_night.py arm-census --plan <staged-plan-path>` from the measurement checkout with its Python interpreter. A staged plan is a plan file outside the supervisor's discovery directory. The command's **exit code**, the integer returned when it finishes, must be 0 before publication; otherwise preserve the output and stop. Follow the runbook's owner-identification instructions, including its explicit override only when the current arming session is not the recorded owner.
>
> For **`REHEARSAL_STUB`**, the plan class that runs a harmless built-in substitute for measurement, this check can classify an **interactive session**, a recognized Claude/T3 host awaiting user-directed work, as not foreign. **Foreign** means outside the proven current arming activation. The exception requires the session to be **idle** under this exact rule: its **process tree**, every child and later descendant reached through parent identifiers, contains no test, measurement, capture, headless agent or unclassified process. A fake test server counts as work. Connection-hosting helpers do not hide their children. Unknown or changing observations fail the check. The command records the root and descendants by **PID**, the numeric process identifier, and start identity, which distinguishes a later process assigned the same number.
>
> The exception is selected from the parsed plan's class in code, not from its name or a command-line override. It does not apply to **`DIAGNOSTIC_NO_PACK`**, a real night without a measurement pack, or **`TRANSACTION_PACK`**, a real night bound to a measurement pack. Nor does it exempt a foreign **headless** Claude session, one executing a print-mode task without interactive steering; only the separately proven current arming activation receives the existing own-process treatment.
>
> All sessions must still close before the **plan span**, the agent-free interval beginning 25 minutes before **`t0`**, the planned measurement start. The unfiltered night census remains unchanged. An agent found at the real night's gate produces **`night_refused_agent_present`**, the recorded refusal reason, and no measurement chain starts. Rehearsals retain their existing harmless-stub behavior and recording of census hits. This arm check grants no exemption during the plan span and changes none of the preceding retry lane's notice or refusal rules.

Keep the diagnostic Purpose, full schedule/notice fields, owner-NO precedence, all four installer outcomes, and verified-uninstall instructions intact. Align new retry-lane links after that predecessor lands; do not re-enumerate or extend its retry class here.

## 4. Test cells, oracles and must-die set

All proposed tests use data fixtures and mocks, not running agent/server processes. A **counterfactual test** compares the same process observation in contexts that must yield different results. “Must die” means an intentional defect must cause the named test assertion to fail; a test that crashes at import or never reaches the assertion does not establish the required coverage.

| Cell / exact proposed test name | Oracle | Must-die mutant |
|---|---|---|
| C01 `ArmCensusTests.test_stub_idle_claude_and_t3_pass_with_evidence` | Separate Claude/versioned-Claude/T3 fixtures with inert descendants: pass; exact exempt root IDs and full descendant IDs retained; paired busy fixture fails | M01: disable exception or return empty evidence |
| C02 `test_identical_idle_tree_is_exempt_only_for_stub` | Same observation/time/owner; stub passes, valid diagnostic and pack fail with that foreign PID. A diagnostic plan ID containing `rehearsal` still fails | M02: remove exact class guard, include diagnostic, or select by plan ID |
| C03 `test_headless_daemons_twins_and_name_lookalikes_are_foreign` | Foreign `claude -p`, attached short print flag, long print forms, daemon/bg hosts/twin, `echo claude`, `notclaude`, unrelated script path all fail; plain/versioned interactive controls pass | M03: substring-match interactive roots or globally exclude headless |
| C04 `test_t3_transport_is_ancestry_bound_and_desktop_apps_stay_foreign` | T3→codex app-server with no work passes stub; same server under ChatGPT or PPID 1 fails; standalone Codex and Claude desktop helpers fail | M04: app-server/global helper exemption without T3 ancestry |
| C05 `test_grandchild_and_sibling_work_invalidates_entire_session` | Idle root→transport→shell→unittest fails and names deepest PID; work in another branch blocks exempting an otherwise idle raw hit; no-descendant control passes | M05: inspect only direct children, only raw hits, or only one branch |
| C06 `test_each_executed_workload_family_blocks` | Literal parameter rows for every family in §3.1, with direct and wrapped/grandchild forms: each fails and identifies workload PID; failure reason/category asserted | M06: independently remove each unittest, pytest, shard, powermetrics, nvidia-smi, driver, campaign, capture, node-worker and MLX rule; either category must change or rejection must fail |
| C07 `test_fake_vllm_script_is_work_at_every_depth` | `python /tmp/.../bin/vllm serve /fake/model` direct/grandchild rejects; Python-script fake sampler rejects; no path/model escape | M07: ignore `/tmp`, `fake`, `mock` or fixture processes |
| C08 `test_wrappers_and_agent_execution_never_look_idle` | env/sudo/nohup/caffeinate; shell `-lc`; Python `-c`; codex options + exec/e; foreign Claude print child all block | M08: unwrap only first word, allow shell `-c` because child not yet spawned, or call codex exec inert transport |
| C09 `test_unclassified_descendant_fails_closed` | Root with unknown executable/module fails `arm_census_unknown`; root alone passes | M09: default unknown to idle |
| C10 `test_arm_exception_ends_at_plan_span_start` | At boundary minus one second a qualifying stub passes; equal/after `t0 − 1500` refuses; no clock rounding tolerance | M10: use `>` instead of `>=`, or use `t0` as cutoff |
| C11 `test_observation_errors_and_tree_changes_are_not_absence` | Parameterized probe errors/output contradictions, malformed PID, missing exact row, permission failure, duplicate IDs, cycles, missing ancestry, PID reuse, exec/reparent, new/departed descendant: nonpass with recorded error; complete stable control passes | M11: skip malformed/vanished rows, trust old PID, accept new tree silently |
| C12 `NightDriverTests.test_arm_census_cli_uses_parsed_plan_and_has_no_night_effects` | Actual `main(['arm-census', ...])`, fake readers, real parsing; stub/diagnostic controls; malformed plan fails; proposed override flags rejected; assert no mkdir, launch, courier or receipt writes | M12: caller-chosen class, default malformed input to stub, or fall through to `run_night`/`dead_man` |
| C13 `test_runbook_final_arm_census_failure_stops_publication` | Extract the bounded final-census shell block and run it with `zsh -f` in a temporary directory, replacing only the census command with a shell function returning 3/2 and publication with a sentinel write: sentinel untouched; exit 0 control reaches sentinel. No installer, census, server or workload executes | M13: `|| true`, swallowed pipeline status, or put census after publication |
| C14 `NightGateTests.test_idle_interactive_hit_still_refuses_real_plan_at_t0` | Pair arm-classifier stub pass with real gate evaluation of the same idle Claude PID at `t0` for diagnostic + pack. Gate refusal exactly `night_refused_agent_present`, C3 FAIL, raw argv/stdout preserved; no agent rows control follows baseline outcome | M14: add idle/owner filtering to `agent_census` or gate, rename code, or continue past refusal |
| C15 `test_stub_gate_records_agent_refusal_without_arm_filtering` | Same idle hit + valid stub at `t0`: actual gate receipt REFUSED, exact `night_refused_agent_present`; no-hit stub produces REHEARSAL_ONLY | M15: apply arm exception to the rehearsal gate branch |
| C16 `NightDriverTests.test_real_idle_agent_hit_refuses_without_chain_or_pack_authoring` and `PackNightProducerTests.test_idle_agent_hit_preserves_initial_refusal_code` | Driver initial raw census hit in a valid real plan: exit 3, result/receipt/refusal exact reason, no Popen chain; pack also no author/prepare/GO. Exact census argv and first-event order pinned | M16: filter driver initial census, ignore its refusal, or prepare pack before census |
| C17 `NightDriverTests.test_idle_agent_appearing_after_go_still_aborts_real_chain` | Initial empty probe followed by idle Claude hit: actual running-census path kills mocked chain group, result `night_aborted_agent_present`, hit retained | M17: change running census to arm filtering or disable `abort_on_census` for real plans |
| C18 existing `test_rehearsal_census_hits_are_observed_without_killing_the_stub` | Existing REHEARSAL_ONLY, hit list and no-kill expectations remain unchanged; add explicit gate receipt reason assertion if missing | M18: “fix” the harmless-stub continuation or erase its hit evidence |
| C19 `ArmIsolationTests.test_production_census_keeps_own_and_foreign_headless_hits` | Actual watchdog production function receives raw `claude -p`, idle Claude, and T3 hits, one per subtest: `empty=False`, exact raw output retained; empty control passes | M19: use `_is_interactive_claude`, handoff ownership or new arm classifier in watchdog production census |
| C20 `ArmCensusTests.test_own_headless_requires_current_ancestry_and_stable_start` | Current owner headless root + census corridor passes all classes; identical foreign headless root fails; stale lock/PPID-1 reuse/unrelated override/generic shell root fail; own sibling test/seat fails | M20: trust PID alone, default missing lock to own, exempt all descendants before checking work |
| C21 `test_arm_discovery_is_case_insensitive_without_changing_night_argv` | Fake runner sees exact arm `-ilf`; uppercase T3 root plus child workload rejects; uppercase idle T3 positive; gate constant remains literal old `-lf` tuple | M21: remove arm `-i`, or change shared plan-span argv |

C13 executes the actual extracted conditional after replacing its two effectful commands, not a Python reimplementation of shell exit semantics. If no zsh is available, mark this cell skipped and report the gap; do not report a source-string check as the behavioral oracle. Its sole shell runs synchronously with a short timeout and is reaped before return. All proposed execution waits for the lead's release; this seat executes none of it. Tests must not derive their workload rows from `arm_census`'s tables: independent literal examples are necessary for omission mutants to bite. M06's category assertions intentionally distinguish known workload from unknown fallback; otherwise deleting a pattern would leave all rejection assertions green.

The contract refuter independently enumerates clauses before opening the map. The execution refuter must try M02, M05, every M06 family deletion, M07, M10, M14, M16, M19 and M20 at minimum, then the remaining listed variants. Removing a rule that falls back to unknown must fail its asserted category, not be falsely reported killed merely because the scenario still refuses. All mutant execution is future lead work under Ed's process-prudence permission, never this seat's work.

## 5. Verification commands and limits

**Executed here:** read-only source/authority inspection; baseline canonical-digest check; Git HEAD/status checks. No test suite, test method, live census, `ps`, `pgrep`, powermetrics, server or installer was run. Process commands above are proposed future command strings, not observed live output.

At implementation intake, the lead verifies the landed base/allowlist, then uses read-only diff and syntax review first:

```sh
git status --short --branch
git diff --check
git diff -- joulewise/arm_census.py scripts/run_night.py tests/test_arm_census.py tests/test_night_gate.py tests/test_run_night.py tests/test_magistrate_watchdog.py docs/process/NIGHT_HANDBACK.md docs/phase_2/derivation_night_runbook.md
```

Use `ast.parse` on changed Python sources without importing them if a syntax-only check is needed. A grep for `runbook template|step-3b|step 3b` is a locator, not permission to rewrite historical traces. Verify the old production census sites and night-code table by diff; avoid whole-tree code generators.

**Proposed focused commands, NOT RUN and NOT AUTHORIZED by this design request.** After the magistrate explicitly releases bounded fixture tests under Ed's prudence constraint:

```sh
python3 -B -m unittest tests.test_arm_census
python3 -B -m unittest tests.test_night_gate.NightGateTests.test_idle_interactive_hit_still_refuses_real_plan_at_t0 tests.test_night_gate.NightGateTests.test_stub_gate_records_agent_refusal_without_arm_filtering
python3 -B -m unittest tests.test_run_night.NightDriverTests.test_arm_census_cli_uses_parsed_plan_and_has_no_night_effects tests.test_run_night.NightDriverTests.test_runbook_final_arm_census_failure_stops_publication tests.test_run_night.NightDriverTests.test_real_idle_agent_hit_refuses_without_chain_or_pack_authoring tests.test_run_night.PackNightProducerTests.test_idle_agent_hit_preserves_initial_refusal_code
python3 -B -m unittest tests.test_run_night.NightDriverTests.test_idle_agent_appearing_after_go_still_aborts_real_chain tests.test_run_night.NightDriverTests.test_rehearsal_census_hits_are_observed_without_killing_the_stub
python3 -B -m unittest tests.test_magistrate_watchdog.ArmIsolationTests
```

Check actual final class/method placement before replay. Do not launch these against today's tree: the new methods do not exist yet. After each named one-site mutant is applied in an authorized isolated implementation tree, rerun its exact method, confirm its oracle fails, restore it and confirm the control passes. No mutation writes to the current design tree.

The repository's canonical `python3 -m unittest discover -s tests` remains **deferred, not waived and not green**: Ed explicitly prohibited running suites in this seat. The lead owns whether/when it can run after the process incident. No live hardware gate is delegated. A bounded later observation of idle and busy UI/session trees may validate structural coverage only; it is not quiet-machine evidence and must not start measurements. Final verification, the twelve-row gate, and merges remain magistrate-owned.

## 6. Out of scope and NEEDS_RULING questions

Out of scope: implementation in this seat; test execution; edits to the installer checkout; canonical checkout, LaunchAgents, night-custody and measurement clones; signaling/closing sessions; starting captures; changes to load/physics/evidence/custody gates; expanding D-180's retry enumeration; remote-control activation; plan-schema/receipt-schema changes; plan-span agent matching or refusals; historical runbook rewrites; re-arming any prior night; commits, push, merge, deployment, notice email; lead bookkeeping outside the granted path.

The complete design is reviewable, but the following choices must be ruled before implementation. None requires extra writes to deliver this brief.

**R1 — What precisely is the approved interactive/T3 surface?** Options: (a) broad substring suppression including arbitrary helpers; (b) true executable/argument recognition, case-insensitive arm discovery, ancestry-bound enumerated idle transports and rejection of unclassified descendants; (c) leaf-only Claude exception and defer T3. **Recommend (b)** with exactly §3.1's initial shapes. Approve `-ilf` only for the new arm command and the limited transport set; preserve the old `-lf` production census. No standalone Codex or ChatGPT/Claude desktop exemption. If actual T3 helpers do not fit those observed/documented forms, collect their command/ancestry evidence read-only and resume with exact additions and paired busy-child refuters. **Blocked work:** final classifier/discovery/helper table and claiming T3's live coverage. The structural design is implementable; its actual helper coverage is PROVISIONAL, not established by the historical synthetic T3 strings.

**R2 — Is the explicitly invoked runbook command the enforcement boundary, or must installation independently call it?** Options: (a) replace live runbook step-3b/final check with a typed-plan arm command; (b) also make every installer invocation perform the census, changing admission and installer test/environment behavior. **Recommend (a)**: acceptance names the runbook precondition, and the class/time/ownership predicates are enforced in code. The pending transaction installer has no current census and owns unrelated rollback/uninstall invariants. This is the smallest change that installs the ruled exception. The runbook remains the publication/notice workflow; an operator who deliberately skips it is outside that procedure, as today. **Blocked work:** final scope and placement; (b) needs a revised explicit allowlist including `joulewise/night_agent_install.py`, its relevant tests and a separate placement ruling before any edit. Do not infer that authority from reading the file.

**R3 — How should prose distinguish the unchanged rehearsal driver from the real-night refusal?** Options: (a) preserve literal claims that any agent kills even the harmless stub; (b) retain gate refusal and existing stub execution/recording, write the precise text dictated above; (c) change rehearsal runtime to stop before its stub. **Recommend (b)**. The existing test intentionally proves rehearsal hits are observed without killing the stub; acceptance says plan-span behavior is untouched. The rule requiring all agents closed before the span remains binding. **Blocked work:** final runbook/handback wording. Option (c) is a separate runtime-policy change, not an A173 fix.

**Next exact step:** the magistrate rules R1–R3, waits for the installer and retry predecessors to land, refreshes the quoted anchors and actual helper evidence, then issues a bounded implementation prompt with the eight exact paths above (or a separately ruled amended scope). Read the clause map before commissioning refuters. Preserve the no-tests restriction until explicitly lifted for the relevant verification step.
