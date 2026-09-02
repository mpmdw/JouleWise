ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — this includes NEVER running `claude -p` yourself; you write the scripts that will, and the magistrate runs them)
GENRE: implementation
WRITE_SCOPE: ["scripts/run_night.py", "scripts/gen_g2_phase_d.py", "scripts/install_night_agent.sh", "scripts/measure_claude_cold_start.sh", "configs/launchd/com.joulewise.night.plist.template", "docs/process/NIGHT_COURIER_PROMPT.md", "tests/test_run_night.py", "tests/test_gen_g2_phase_d.py"]

# WO-2 — night driver, chain emitter, LaunchAgent, courier (D-169 stage 1)

Checkout: `/Users/edr/code/JouleWise-wt-night-driver` (branch
`feat/2026-09-01-night-driver`, head `d433fd67` = PR #257's head, so the
runsheet's G2-a section and `scripts/gen_g2_phase_d.py` are the #257 versions).
Linked worktree: do NOT commit; the magistrate commits. `TMPDIR` = a
subdirectory of
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/`
that you create. Do NOT run the canonical `unittest discover`; run only
`python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d` (plus
`tests.test_check_window_provenance`, which asserts runsheet bytes — it must
still pass because you do not change the runsheet). Avoid the substring `t3`
in any argv, label, file name or log line you create: the agent census is
`pgrep -lf "codex|claude|t3"` and a match would refuse the night.

Authority: the ruling
`/Users/edr/code/JouleWise/docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`
(absolute path in the MAIN checkout; not in your worktree; if unreadable,
stop with NEEDS_RULING). Read §1, §2 R-2/R-3/R-5/R-6/R-7/R-9, §3, §7.
The gate library `joulewise/night_gate.py` is being written by ANOTHER seat
in parallel; its interface is fixed and reproduced below — code against it
and, for your tests, ship a minimal fake in `tests/test_run_night.py`
(`import joulewise.night_gate` may fail in this tree: guard the import and
skip only the tests that need the real module, never the driver's own).

## The gate interface you code against (fixed)

```python
from joulewise.night_gate import (SCHEMA, RESULT_SCHEMA, RECEIPT_CLASSES, AGENT_CENSUS_ARGV,
    NIGHT_GATE_REASON_CODES, ProbeResult, Probes, NightPlan, Refusal, Receipt,
    agent_census, evaluate_night, validate_receipt)
# Probes(run, now_epoch_s, monotonic_ns, read_text, checkout_head); run(argv)->ProbeResult(argv, exit_code, stdout, stderr, monotonic_ns)
# NightPlan.from_mapping(dict) ; fields: plan_id, receipt_class, t0_epoch_s, window_max_s, authored_epoch_s,
#   repo_head, chain_path, chain_sha256_path, custody_root, registration_path
# evaluate_night(plan, probes) -> Receipt(schema, receipt_class, plan_id, verdict "GO"|"REFUSED"|"REHEARSAL_ONLY",
#   conditions, refusal: Refusal(reason, detail, evidence)|None, authored_monotonic_ns) ; Receipt.to_json_bytes()
# agent_census(probes) -> (ProbeResult, Refusal|None)
```

## Deliverable A — `scripts/gen_g2_phase_d.py --emit-chain OUT --night-date YYYYMMDD`

The G2-a section of the runsheet (`## G2-a — first machine evening` up to the
next `## ` heading) plus the `## Tree and fixed variables` section hold the
executable night. Inventory every ```sh / ```zsh block in those two sections
(report the line ranges). The emitted chain is ONE executable zsh file:
`#!/bin/zsh` + `set -euo pipefail` + the fixed-variables export block + the
G2-a export block + the generated bracket block + the summarizer block, in
runsheet order, each preceded by a comment `# runsheet L<a>-<b>`. The
desk-producer block (`generate_g2a_probe_inputs.py build-probes / bind-window`,
runsheet ~L283-294) is NOT in the chain: it runs at arm time with agents
present; the chain instead asserts its outputs exist (`test -f` on
`$G2A_INPUT_INVENTORY`, `$G2A_FROZEN_PLAN`, `$G2A_PROMPT_LADDER`) before the
bracket. `--night-date` replaces every occurrence of the literal `20260830`
in the export block (and only there) with the given date; the identity test
uses `20260830` and asserts the emitted blocks are byte-equal to the runsheet
blocks (extract them independently in the test with a fence parser, do not
call the same function twice). Also write `OUT.sha256` (`<hex>  <basename>`
line). Existing behaviour of the script (`--check`, in-place update) is
unchanged; `tests/test_gen_g2_phase_d.py` may exist already — extend it.

## Deliverable B — `scripts/run_night.py`

Subcommands: `run --plan PLAN.json` (the timer entry), `dead-man --plan`
(07:00 entry: only the courier step, only if `courier.sent` is absent),
`rehearse --plan` (identical to `run` except the chain is replaced by
`configs/launchd/`-free stub: an inline `/bin/zsh -c 'sleep 2; echo REHEARSAL'`,
and the plan's class must be `REHEARSAL_STUB`; a GO can never result).

`run` sequence (each step appends a line to `$custody_root/night.log`, and
every artefact below is written under `$custody_root/night/`):
1. Build real `Probes` (subprocess with 30 s timeout per probe → ProbeError
   on timeout; `git -C <repo> rev-parse HEAD` for checkout_head).
2. `receipt = evaluate_night(plan, probes)`; write `receipt.json`
   (`to_json_bytes`). If `verdict != "GO"` → write `refusal.json`, go to 6.
3. Verify chain: sha256 of `plan.chain_path` bytes == sidecar (the gate
   already did; do it again here in the driver — belt and braces — and
   refuse `night_chain_digest_mismatch` if not).
4. Run the chain ONCE: `subprocess.Popen(["/bin/zsh", chain_path], start_new_session=True, stdout=chain.stdout.log, stderr=chain.stderr.log, env=os.environ|{"NIGHT_PLAN_ID": plan_id})`.
   While it runs, every `CENSUS_INTERVAL_S = 30` call `agent_census(probes)`
   and append each result to `censuses.jsonl`; on a refusal, SIGTERM the
   process GROUP, wait ≤ 30 s, SIGKILL, record `night_aborted_agent_present`
   with the census lines. D-078: no retry of the chain under any outcome.
5. Write `result.json` (schema RESULT_SCHEMA: plan_id, receipt_class,
   verdict, chain_exit_code|None, aborted_reason|None, started/ended epoch +
   monotonic, chain_sha256, census_count, artefact list with sha256s).
6. Durable record: `git -C <repo> checkout -B night-results/<night-date>`
   is FORBIDDEN (the checkout may hold the loop's state). Instead: copy
   `receipt.json`, `refusal.json`, `result.json`, `censuses.jsonl`,
   `night.log` into `docs/process_traces/night-results/<night-date>/` in a
   fresh clone under `$custody_root/results-clone` (`git clone --depth 1
   --branch main <origin-url> results-clone`), commit on branch
   `night-results/<night-date>`, push. Failures here are logged, never fatal.
7. Courier: launch `COURIER_ARGV` (module constant; see below) with
   `start_new_session=True`; the courier's FIRST act (its prompt says so)
   writes `courier.heartbeat`. Wait up to `COURIER_DEADLINE_S` (module
   constant, initial value 600; the magistrate resets it from the cold-start
   measurement) for the heartbeat; on timeout kill the group and retry with
   backoff `COURIER_BACKOFF_S = (60, 180, 600)` — at most 3 attempts total.
   Each attempt appends to `courier.attempts.jsonl`. Stand down on proof;
   never wait on the courier's exit.
8. Exit 0 if GO and chain rc 0; exit 3 on refusal; exit 4 on abort; exit 5
   on chain rc != 0 (documented in `--help`).

`COURIER_ARGV = ("/usr/bin/env", "claude", "-p", <prompt text read from docs/process/NIGHT_COURIER_PROMPT.md with {custody_root} and {plan_id} substituted>, "--output-format", "text", "--allowedTools", "Read,Glob,Grep,Bash,Edit,Write,mcp__claude_ai_Gmail__send_message")`
— exact tool names are the magistrate's; keep them as a single module
constant `COURIER_ALLOWED_TOOLS`. Do not invoke it in tests: assert the argv
shape only.

## Deliverable C — `docs/process/NIGHT_COURIER_PROMPT.md`

The fixed courier prompt (Ed's writing standard: plain words, every term
defined at first use). It must instruct, in order: (1) first act — write
`{custody_root}/night/courier.heartbeat` containing the courier pid and
`date +%s`; (2) read `docs/process/NIGHT_HANDBACK.md` (the magistrate writes
it before an armed night; the file names the purpose, the result paths, the
next lane), then `{custody_root}/night/result.json` and `receipt.json` or
`refusal.json`; (3) email Ed at `claude.ai.copper531@passmail.net` a plain
summary (verdict, chain exit code, refusal reason + detail if any, the
results branch name), then write `courier.sent`; (4) continue with the
handback's next lane under the standing loop rules. Under 60 lines.

## Deliverable D — LaunchAgent template + installer

`configs/launchd/com.joulewise.night.plist.template`: Label
`com.joulewise.night`; `ProgramArguments` → `/usr/bin/env python3
<repo>/scripts/run_night.py run --plan <plan>`; `StartCalendarInterval`
{Hour, Minute} from placeholders `@@HOUR@@ @@MINUTE@@`; `StandardOutPath`/
`StandardErrorPath` under `@@CUSTODY_ROOT@@/night/launchd.{out,err}`;
`RunAtLoad` false; a second plist entry (or a second template
`com.joulewise.night.deadman.plist.template`, your call — say which) at
07:00 running `dead-man`. `scripts/install_night_agent.sh --plan PLAN.json
--hour H --minute M [--uninstall]`: renders both plists into
`~/Library/LaunchAgents/`, `launchctl bootout gui/$UID <label>` if loaded,
`launchctl bootstrap gui/$UID <plist>`, then `launchctl print gui/$UID/<label>`
to prove it; NO sudo anywhere (`grep -c sudo` must be 0 — test it). Refuses
if the plan's `repo_head` != `git rev-parse HEAD`.

## Deliverable E — `scripts/measure_claude_cold_start.sh`

Runs `claude -p 'Reply with exactly the word READY.' --output-format text`
five times, timing each with `date +%s%N`, then once with the prompt
`List the exact names of the tools available to you whose name contains
Gmail, one per line, nothing else.`; writes `cold_start.json` (five
durations ms, median, the Gmail tool-name list) to the path given as `$1`.
The MAGISTRATE runs it (you never do).

## Tests

`tests/test_run_night.py` (fake gate module injected via `sys.modules` if the
real one is absent; fake `subprocess` via a recording shim; a temp custody
root): refusal path writes receipt+refusal and never spawns the chain;
GO path spawns the chain exactly once and never twice on non-zero rc
(D-078); census refusal mid-chain terminates the group and records the
abort; courier retries follow (60,180,600) and stop after 3; dead-man skips
when `courier.sent` exists; rehearse refuses a non-REHEARSAL_STUB plan; exit
codes; the results-clone step failing does not change the exit code.
`tests/test_gen_g2_phase_d.py`: block inventory, identity with date
20260830, date substitution confined to the export block, sidecar format.

## Report

Envelope: first fenced ```json block, `claude-codex-report/v1`, genre
`implementation`; then: block inventory table (runsheet line ranges → in
chain / excluded, why), any deviation from this brief (named, with reason),
test counts and the exact commands run, and the list of every module
constant the magistrate may need to reset (`COURIER_DEADLINE_S`,
`COURIER_BACKOFF_S`, `CENSUS_INTERVAL_S`, `COURIER_ALLOWED_TOOLS`). Under
140 lines after the envelope.
