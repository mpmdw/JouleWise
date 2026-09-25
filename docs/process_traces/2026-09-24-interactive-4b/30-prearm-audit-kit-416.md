# Full-system audit kit (directive #416, amended 2026-09-25: runs AFTER W1/W2 pass, BEFORE any claim-bearing run)

This kit is ready before its trigger. The trigger is the magistrate's message "CLAIM-RUN WORK COMPLETE" (W1/W2 issued and the headline pipeline frozen), carrying the frozen sha **S**, the in-scope list and the W1/W2 bundle paths. Ed amended the order on 2026-09-25 (issue #416 comment): passing windows are consistency evidence, not correctness evidence, so the audit stays mandatory before claim runs. Auditors must independently re-derive the W1/W2 calibration from the raw bundles. Directive #416 plus Ed's 2026-09-25 follow-up: "do that unless that limits its audit ability in any way. the auditer should be able to launch subagents to speedily do the audits, with workflows authorized for the audits".

## Seats

| Seat | How it runs | Effort | Fan-out |
|---|---|---|---|
| Fable 5.1 lead | headless `claude -p` session in a detached worktree at S | `--effort xhigh` (smoke-tested 2026-09-25: resolves to `claude-fable-5-1`) | Agent subagents and the Workflow tool, authorized by Ed for this audit |
| Opus 5.5 lead | headless `claude -p` session in a detached worktree at S | `--effort xhigh` | the same |
| Astra 6 | `codex-run-v3 -m gpt-6-astra --effort xhigh` in a detached worktree at S | xhigh, as Ed specified. Codex spawns subagents only at `ultra` (rule 10); switch this seat to ultra if Ed wants Astra to fan out too. | none at xhigh |

**Headless does not limit the audit.** Each lead is a full Claude Code session with an explicit effort level, subagents and workflows. **One known hazard:** a headless session exits at the end of its turn and kills its children (memory headless-turn-end-kills-seats). The brief therefore obliges each lead to hold with bounded foreground waits until every subagent and workflow has returned, before it writes its final answer.

## Launch (the lead runs this from a session that stays alive)

```zsh
S=<frozen sha>; for f in fable opus astra; do git -C /Users/edr/code/JouleWise worktree add --detach /Users/edr/code/wt-audit416-$f $S; done
mkdir -p /tmp/audit416
TOOLS="Read,Glob,Grep,Bash,Agent,Task,Workflow,Skill,Monitor,TaskCreate,TaskUpdate,TaskList"
cd /Users/edr/code/wt-audit416-fable && claude -p "$(cat /tmp/audit416/brief-fable.md)" --model fable --effort xhigh \
  --permission-mode auto --allowedTools "$TOOLS" --output-format stream-json --verbose > /tmp/audit416/fable.jsonl 2>&1
cd /Users/edr/code/wt-audit416-opus  && claude -p "$(cat /tmp/audit416/brief-opus.md)"  --model opus  --effort xhigh \
  --permission-mode auto --allowedTools "$TOOLS" --output-format stream-json --verbose > /tmp/audit416/opus.jsonl 2>&1
cd /Users/edr/code/wt-audit416-astra && CODEX_SERVICE_TIER=default codex-run-v3 /tmp/audit416/astra.md --timeout 14400 \
  -C /Users/edr/code/wt-audit416-astra -s workspace-write -m gpt-6-astra --effort xhigh --genre review --write-scope '[]' "$(cat /tmp/audit416/brief-astra.md)"
```

Each command runs as its own tracked background job. The three run concurrently.

## Common brief (identical for every seat apart from its header)

> **ROLE.** An independent, BLIND pre-arm auditor of the JouleWise measurement system at frozen sha S (this worktree). You audit alone: do not read other auditors' outputs, `/tmp/audit416/*` apart from your own brief and scratch, or earlier audit records' conclusions about the areas you audit, before you have formed your own findings. Your findings decide whether the first claim-bearing (headline) runs may start, and whether W1/W2 must be re-run.
>
> **SCOPE.** Every path that can change a measured or claimed number, or can let a bad window through:
> 1. the instrument adapters (powermetrics capture, parsing, clock anchoring, dwell, the cadence probe);
> 2. calibration derivation and issuance (Revision 5, issuer, acceptance rules);
> 3. night machinery (evidence-night prepare, install, launch context/ProcessType, t0 census and quiet admission, driver, chain, harvest, courier, refusal and successor rules);
> 4. reduction (integration, idle subtraction, uncertainty and bound terms, the scored reducer);
> 5. analysis and claim code (claim gate v2 wiring, J/correct, the equivalence and power rules);
> 6. the OS-interaction facts established on 2026-09-24/25: launchd ProcessType, timer coalescing, Spotlight, network time, display state (records in docs/process_traces/2026-09-24-interactive-4b/).
>
> The magistrate's in-scope list for S and the W1/W2 bundle paths are appended below. Re-derive the issued calibration from the raw W1/W2 bundles with your own code, and compare it with what the issuer produced.
>
> **WHAT TO LOOK FOR.**
> - Physics and metrology errors.
> - Silent-wrong paths: a number that is wrong with no refusal.
> - Gates that are unsized to the instrument (too loose OR too tight).
> - Refusal paths that fail open.
> - Custody or identity gaps between what was measured and what is claimed.
> - Test suites that would not catch the defect (run mutation probes where cheap).
> - Anything that differs between the frozen head and the ruled texts it claims to implement.
>
> **HOW.**
> - Fan out: split the scope across subagents, and use the Workflow tool for mechanical multi-site sweeps. Ed authorized Workflow use for this audit, verbatim above.
> - Verify every candidate finding with executed evidence (a test, a script, a reproduction) before reporting it.
> - Severity: BLOCKER (W1 must not arm), SHOULD_FIX, NIT.
>
> **FENCES.** Read-only apart from scratch `/tmp/audit416/<seat>/`.
> - NEVER run launchctl, sudo, systemsetup, powermetrics, pmset or caffeinate. Never run a runner or night command live, and never run `joulewise run`.
> - Never touch `/Users/edr/night-custody`, any measurement clone, `~/Library/LaunchAgents` or `/Users/edr/code/JouleWise`.
> - No measurement hardware.
> - Do not call other auditors or the magistrate.
>
> **HOLD RULE (headless).** Never end your turn while any subagent, workflow or background command you started is still running. Wait with bounded foreground waits or Monitor until all have returned. Your final message is your report, and ending it kills anything still running.
>
> **REPORT** (final message, ≤ 2,500 words):
> - a table of findings: id, severity, file:line, one-sentence defect, the concrete failure scenario, the executed evidence (command and tail);
> - a separate list of what you checked and found sound;
> - your verdict: ARM / ARM AFTER LISTED BLOCKERS / DO NOT ARM.

## Synthesis (after all three return)

1. The lead merges the findings, dedupes them across families, and keeps each family's attribution.
2. Every BLOCKER gets a refuter from a **different** family: fresh, with only the finding plus the code. Split verdicts are adjudicated by a cold Fable gate.
3. Confirmed BLOCKERs are fixed under their tier's gate (#415) before W1 arms. A BLOCKER disputed as not load-bearing goes to a cold gate.
4. The audit record is filed next to the magistrate's W1 records, and the arm notice links it.
