# 04b — A173 ARM-CENSUS-IDLE-INTERACTIVE-01 design rulings (magistrate b0ae8462, 2026-09-15 21:05 PDT)

Inputs: Astra design brief (04), fresh Opus contract-lens refuter (04a, with one live `ps` read). All three of the
refuter's blockers are ADOPTED; net verdict AMEND. Ed's directive of this evening applies directly: windows must never be
made artificially scarce, so a classifier that manufactures arm refusals is the wrong polarity.

**Blocker 1 (adopted) — the enumerated-inert-set design refuses the case the lane exists to permit.** Live evidence:
Claude Code spawns a `zsh -c …` child per tool call under the interactive root, plus `ugrep`, `codex-code-mode-host`
and similar helpers; under "everything not enumerated blocks" no real idle session ever passes.

**Blocker 2 (adopted) — no tightening of the REAL-night arm path.** The new census command's non-zero exit blocks
publication ONLY for a `REHEARSAL_STUB` plan; for every other class it is diagnostic output and the existing runbook
step-3b prose rule (all agents closed) and the untouched t0 plan-span refusal stay exactly as they are. A173 is a stub
EXEMPTION, not a new real-night gate.

**Blocker 3 (adopted) — D-161 polarity.** A wrong "idle" verdict for a stub costs one rehearsal (plan-span census
untouched; D-180 cl.2 pre-authorises the retry) and no physics, evidence or registration; so UNKNOWN reads as IDLE.
Dropped: `arm_census_unknown`, tree-change re-observation, start-identity proofs, the lock/`lstart` ownership bridge,
`-ilf` discovery (the arm may not see more than `AGENT_CENSUS_ARGV` sees), and the inert-transport table.

**R1 — REJECT (b); ADOPT (d), the workload-positive classifier.** Root = `_is_interactive_claude` (already rejects
`-p`, `--print*`, daemon, bg-spare, bg-pty-host) AND `basename(executable) == "claude"`; the only T3 root shape shipped
is a Node process whose script operand ends in `/t3-code/dist/cli.js` (no T3 process exists on the machine today — every
Electron-helper rule stays unclaimed until observed). Descendant closure from the kernel inventory
(`DarwinProcessSource.inventory()` / `read_exact`, true executable + argv). BUSY iff any descendant matches the workload
table: `unittest`/`pytest`/`scripts/shard_tests.py`, `powermetrics`, `nvidia-smi`, `scripts/run_night.py`,
`scripts/run_campaign.py`, `scripts/capture_t0_step.py`, `chain.zsh`, `-m joulewise*`, `vllm`/`mlx` serve or `-m vllm…`/
`-m mlx…`, `codex … exec` (options before OR after the subcommand), any `claude … -p`/`--print*`. Everything else is
idle. Lost, and accepted: a future runner absent from the table reads idle at arm and costs one stub refused at t0.

**R2 — ADOPT (a) with the Blocker-2 amendment.** The explicitly invoked runbook command is the boundary; no census
inside `night_agent_install.py` (that file is under active fix rounds; a census there buys a cross-lane conflict and a
real-night admission refusal for zero acceptance value).

**R3 — ADOPT (b), prose trimmed.** The rehearsal driver's observed-but-not-killed stub behaviour
(`test_rehearsal_census_hits_are_observed_without_killing_the_stub`) is deliberate and stays. Terms are defined ONCE
in the runbook's existing first-use table; NIGHT_HANDBACK states the rule and cites the runbook section.

**Placement and own-activation.** New `joulewise/arm_census.py` with its own `main(argv)`, invoked by the runbook as
`python3 -m joulewise.arm_census --plan "$STAGED_PLAN"`; class selection on `plan.receipt_class` via
`NightPlan.from_mapping` only (no flag, env var or plan-id path — keep the brief's C02). "Own" = the caller's own PPID
chain (`os.getpid()` upward), never the magistrate lock. `scripts/run_night.py` is OUT of the production WRITE_SCOPE. Add a
structural test that `joulewise/night_gate.py` and `scripts/run_night.py` never import `arm_census` (kills the
"wired into the night gate later" class); keep C15 (a valid stub still refuses at t0) as the plan-span oracle.
WRITE_SCOPE for the implementation seat: `joulewise/arm_census.py`, `tests/test_arm_census.py`,
`tests/test_run_night.py` (C16–C18 pins only), `docs/phase_2/derivation_night_runbook.md`, `docs/process/NIGHT_HANDBACK.md`.
Sequencing: after A172 lands (D-181 cl.1 order), from the post-merge head.

Three-seat note: Astra design + Opus refuter at this stage; the blind Fable seat is deferred to the lane's cold gate.
